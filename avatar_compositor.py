"""
Character Avatar Compositor

Composites a character image onto a gradient portal background using SVG shapes.
Structure: Portal (bottom) → Masked Character (top)
"""

import re
import os
from PIL import Image, ImageChops
import requests
from io import BytesIO
from dataclasses import dataclass
from typing import Tuple

# Optional: cairosvg for SVG rendering
try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass
class PortalGradient:
    """Defines the linear gradient colors for the portal (top-right to bottom-left)."""
    start_color: str  # Hex color at top-right
    end_color: str    # Hex color at bottom-left

    @classmethod
    def orange(cls) -> "PortalGradient":
        """Default orange gradient matching the original design."""
        return cls(start_color="#CE782D", end_color="#E1A371")

    @classmethod
    def blue(cls) -> "PortalGradient":
        return cls(start_color="#2D7ECE", end_color="#71A3E1")

    @classmethod
    def green(cls) -> "PortalGradient":
        return cls(start_color="#2DCE78", end_color="#71E1A3")

    @classmethod
    def purple(cls) -> "PortalGradient":
        return cls(start_color="#782DCE", end_color="#A371E1")

    @classmethod
    def red(cls) -> "PortalGradient":
        return cls(start_color="#CE2D2D", end_color="#E17171")


@dataclass
class AvatarConfig:
    """Configuration for avatar generation.

    Based on Figma export - both SVGs share 340x341 coordinate system.
    """
    output_size: Tuple[int, int] = (340, 341)
    portal_size: Tuple[int, int] = (340, 341)   # Same as output (shared coordinate system)
    mask_size: Tuple[int, int] = (340, 341)     # Same as output (shared coordinate system)
    portal_offset: Tuple[int, int] = (0, 0)     # No offset needed - same coordinate system
    mask_offset: Tuple[int, int] = (0, 0)       # No offset needed - same coordinate system
    character_offset: Tuple[int, int] = (-70, -40)
    character_size: Tuple[int, int] = (449, 804)  # 1.1x original (408, 731)
    character_rotation: float = 3.0  # Counter-clockwise
    face_position: float = 0.0  # 0=top, 0.5=center, 1=bottom - where to crop from


def load_svg_with_gradient(svg_path: str, gradient: PortalGradient) -> bytes:
    """Load SVG and replace gradient colors."""
    with open(svg_path, "r") as f:
        svg_content = f.read()

    # Replace the gradient stop colors (handles both old and new gradient IDs)
    svg_content = re.sub(
        r'stop-color="#CE782D"',
        f'stop-color="{gradient.start_color}"',
        svg_content
    )
    svg_content = re.sub(
        r'stop-color="#E1A371"',
        f'stop-color="{gradient.end_color}"',
        svg_content
    )

    return svg_content.encode('utf-8')


def svg_to_png(svg_bytes: bytes, width: int, height: int) -> Image.Image:
    """Convert SVG bytes to PIL Image."""
    if not HAS_CAIROSVG:
        raise ImportError("cairosvg is required for SVG rendering. Install with: pip install cairosvg")

    png_bytes = cairosvg.svg2png(
        bytestring=svg_bytes,
        output_width=width,
        output_height=height
    )
    return Image.open(BytesIO(png_bytes)).convert("RGBA")


def load_character_image(source) -> Image.Image:
    """Load character image from URL, file path, or PIL Image."""
    # If it's already a PIL Image, just convert to RGBA
    if isinstance(source, Image.Image):
        return source.convert("RGBA")

    # If it's a string, treat as URL or file path
    if isinstance(source, str):
        if source.startswith(("http://", "https://")):
            response = requests.get(source, timeout=30)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
        else:
            img = Image.open(source)
        return img.convert("RGBA")

    raise ValueError(f"Unsupported source type: {type(source)}")


def create_mask_from_svg(svg_path: str, size: Tuple[int, int]) -> Image.Image:
    """Create a mask image from SVG (white shape on transparent)."""
    with open(svg_path, "r") as f:
        svg_content = f.read()

    # Replace any fill with white (cairosvg doesn't understand CSS variables)
    svg_content = re.sub(r'fill="[^"]*"', 'fill="white"', svg_content)

    png_bytes = cairosvg.svg2png(
        bytestring=svg_content.encode('utf-8'),
        output_width=size[0],
        output_height=size[1]
    )

    img = Image.open(BytesIO(png_bytes)).convert("RGBA")
    # Extract the alpha channel as the mask
    return img.getchannel("A")


def composite_avatar(
    character_source: str,
    gradient: PortalGradient,
    config: AvatarConfig = None,
    portal_svg: str = None,
    mask_svg: str = None
) -> Image.Image:
    """
    Composite a character image onto a gradient portal background.

    Args:
        character_source: URL or file path to character image
        gradient: PortalGradient defining the portal colors
        config: Optional AvatarConfig for customization
        portal_svg: Path to portal SVG (defaults to portal.svg in script dir)
        mask_svg: Path to mask SVG (defaults to mask.svg in script dir)

    Returns:
        RGBA image of the complete avatar
    """
    if config is None:
        config = AvatarConfig()

    if portal_svg is None:
        portal_svg = os.path.join(SCRIPT_DIR, "portal.svg")
    if mask_svg is None:
        mask_svg = os.path.join(SCRIPT_DIR, "mask.svg")

    # Create the base canvas
    canvas = Image.new("RGBA", config.output_size, (0, 0, 0, 0))

    # 1. Render portal SVG with custom gradient
    portal_svg_bytes = load_svg_with_gradient(portal_svg, gradient)
    portal_img = svg_to_png(portal_svg_bytes, config.portal_size[0], config.portal_size[1])

    # Paste portal onto canvas (centered)
    portal_x = (config.output_size[0] - config.portal_size[0]) // 2
    portal_y = (config.output_size[1] - config.portal_size[1]) // 2
    canvas.paste(portal_img, (portal_x, portal_y), portal_img)

    # 2. Load and prepare character image
    character = load_character_image(character_source)

    # Scale character using "cover" logic - fill the target area, crop excess
    target_width, target_height = config.character_size
    img_width, img_height = character.size

    # Calculate scale to cover the target area
    scale = max(target_width / img_width, target_height / img_height)
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    character = character.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Crop to target size
    # face_position: 0.0 = top of image, 0.5 = center, 1.0 = bottom
    face_position = getattr(config, 'face_position', 0.3)  # Default to upper third
    left = (new_width - target_width) // 2
    max_top = new_height - target_height
    top = int(max_top * face_position)
    character = character.crop((left, top, left + target_width, top + target_height))

    # Apply rotation if specified (PIL: positive = counter-clockwise, negative = clockwise)
    if hasattr(config, 'character_rotation') and config.character_rotation != 0:
        character = character.rotate(
            config.character_rotation,  # -2 degrees = clockwise rotation
            expand=True,
            resample=Image.Resampling.BICUBIC
        )

    # 3. Create mask from SVG
    mask = create_mask_from_svg(mask_svg, config.mask_size)

    # 4. Create an expanded work area to handle negative offsets
    expand_left = abs(min(0, config.mask_offset[0], config.character_offset[0]))
    expand_top = abs(min(0, config.mask_offset[1], config.character_offset[1]))
    expanded_size = (
        config.output_size[0] + expand_left * 2 + 200,  # Extra padding
        config.output_size[1] + expand_top * 2 + 200
    )

    # Position character on expanded canvas
    char_x = expand_left + config.character_offset[0]
    char_y = expand_top + config.character_offset[1]

    # Position mask on expanded canvas
    mask_x = expand_left + config.mask_offset[0]
    mask_y = expand_top + config.mask_offset[1]

    # Create full-size mask
    full_mask = Image.new("L", expanded_size, 0)
    full_mask.paste(mask, (mask_x, mask_y))

    # Create character on expanded canvas, preserving its alpha
    char_expanded = Image.new("RGBA", expanded_size, (0, 0, 0, 0))

    # Paste character pixels (RGB only first, then handle alpha separately)
    # Create a temp image to hold the character
    temp = Image.new("RGBA", expanded_size, (0, 0, 0, 0))
    temp.paste(character, (char_x, char_y))

    # Get the character's original alpha
    char_orig_alpha = temp.getchannel("A")

    # Combine character alpha with mask (both must be true for pixel to show)
    final_alpha = ImageChops.multiply(char_orig_alpha, full_mask)

    # Apply combined alpha to character layer
    char_expanded = temp.copy()
    char_expanded.putalpha(final_alpha)

    # Crop back to output size
    crop_box = (expand_left, expand_top,
                expand_left + config.output_size[0],
                expand_top + config.output_size[1])
    char_layer = char_expanded.crop(crop_box)

    # 5. Composite masked character onto canvas (above portal)
    canvas = Image.alpha_composite(canvas, char_layer)

    return canvas


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python avatar_compositor.py <character_image> [output_path]")
        print("\nExample:")
        print("  python avatar_compositor.py character.png avatar.png")
        print("  python avatar_compositor.py https://example.com/char.png")
        sys.exit(1)

    character_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "avatar_output.png"

    # Create avatar with default orange gradient
    avatar = composite_avatar(
        character_source=character_path,
        gradient=PortalGradient.orange()
    )
    avatar.save(output_path, "PNG")
    print(f"Avatar saved to {output_path}")

    # Create variants with different gradients
    for name, gradient in [
        ("blue", PortalGradient.blue()),
        ("green", PortalGradient.green()),
        ("purple", PortalGradient.purple()),
    ]:
        variant = composite_avatar(
            character_source=character_path,
            gradient=gradient
        )
        variant_path = output_path.replace(".png", f"_{name}.png")
        variant.save(variant_path, "PNG")
        print(f"Variant saved to {variant_path}")
