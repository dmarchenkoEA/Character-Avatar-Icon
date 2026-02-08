"""
Character Avatar Compositor

Composites a character image onto a portal background with masking.
Supports both gradient fills and image fills for the portal.
"""

import re
import os
from PIL import Image, ImageChops, ImageDraw
import requests
from io import BytesIO
from dataclasses import dataclass
from typing import Tuple, Optional, Union

# Optional: cairosvg for SVG rendering
try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass
class PortalGradient:
    """Defines the linear gradient colors for the portal."""
    start_color: str  # Hex color at top-right
    end_color: str    # Hex color at bottom-left

    @classmethod
    def orange(cls) -> "PortalGradient":
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
    """Configuration for avatar generation."""
    output_size: Tuple[int, int] = (340, 341)
    portal_size: Tuple[int, int] = (340, 376)   # Scaled from 230x254
    mask_size: Tuple[int, int] = (340, 472)     # Scaled from 230x319
    portal_offset: Tuple[int, int] = (0, 38)    # Portal slightly lower
    mask_offset: Tuple[int, int] = (0, -48)     # Mask extends above
    character_offset: Tuple[int, int] = (-70, -40)
    character_size: Tuple[int, int] = (449, 804)  # 1.1x original
    character_rotation: float = 3.0
    face_position: float = 0.0


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_gradient_image(size: Tuple[int, int], gradient: PortalGradient) -> Image.Image:
    """Create a linear gradient image (top-right to bottom-left)."""
    width, height = size
    img = Image.new("RGB", size)

    start_rgb = hex_to_rgb(gradient.start_color)
    end_rgb = hex_to_rgb(gradient.end_color)

    for y in range(height):
        for x in range(width):
            # Diagonal gradient from top-right to bottom-left
            t = ((width - x) + y) / (width + height)
            r = int(start_rgb[0] * (1 - t) + end_rgb[0] * t)
            g = int(start_rgb[1] * (1 - t) + end_rgb[1] * t)
            b = int(start_rgb[2] * (1 - t) + end_rgb[2] * t)
            img.putpixel((x, y), (r, g, b))

    return img


def load_shape_mask(shape_path: str, size: Tuple[int, int]) -> Image.Image:
    """Load a shape mask from PNG or SVG file."""
    if shape_path.endswith('.svg'):
        if not HAS_CAIROSVG:
            raise ImportError("cairosvg required for SVG. Install with: pip install cairosvg")

        with open(shape_path, "r") as f:
            svg_content = f.read()

        # Replace fill with white for mask
        svg_content = re.sub(r'fill="[^"]*"', 'fill="white"', svg_content)

        png_bytes = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=size[0],
            output_height=size[1]
        )
        img = Image.open(BytesIO(png_bytes)).convert("RGBA")
        return img.getchannel("A")
    else:
        # PNG shape - use alpha channel or convert to grayscale
        img = Image.open(shape_path)
        if img.mode == 'RGBA':
            mask = img.getchannel("A")
        elif img.mode == 'L':
            mask = img
        else:
            mask = img.convert("L")

        # Resize to target size
        if mask.size != size:
            mask = mask.resize(size, Image.Resampling.LANCZOS)

        return mask


def create_portal_with_fill(
    shape_path: str,
    size: Tuple[int, int],
    fill: Union[PortalGradient, str, Image.Image]
) -> Image.Image:
    """
    Create portal image with shape and fill.

    Args:
        shape_path: Path to portal shape (PNG or SVG)
        size: Output size
        fill: PortalGradient, image path, or PIL Image for the fill
    """
    # Load shape mask
    shape_mask = load_shape_mask(shape_path, size)

    # Create or load fill
    if isinstance(fill, PortalGradient):
        fill_img = create_gradient_image(size, fill)
    elif isinstance(fill, str):
        # Load image from path or URL
        if fill.startswith(("http://", "https://")):
            response = requests.get(fill, timeout=30)
            response.raise_for_status()
            fill_img = Image.open(BytesIO(response.content))
        else:
            fill_img = Image.open(fill)
        fill_img = fill_img.convert("RGB").resize(size, Image.Resampling.LANCZOS)
    elif isinstance(fill, Image.Image):
        fill_img = fill.convert("RGB").resize(size, Image.Resampling.LANCZOS)
    else:
        raise ValueError(f"Unsupported fill type: {type(fill)}")

    # Apply shape mask to fill
    result = Image.new("RGBA", size, (0, 0, 0, 0))
    result.paste(fill_img, (0, 0))
    result.putalpha(shape_mask)

    return result


def load_character_image(source) -> Image.Image:
    """Load character image from URL, file path, or PIL Image."""
    if isinstance(source, Image.Image):
        return source.convert("RGBA")

    if isinstance(source, str):
        if source.startswith(("http://", "https://")):
            response = requests.get(source, timeout=30)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
        else:
            img = Image.open(source)
        return img.convert("RGBA")

    raise ValueError(f"Unsupported source type: {type(source)}")


def composite_avatar(
    character_source,
    fill: Union[PortalGradient, str, Image.Image] = None,
    config: AvatarConfig = None,
    portal_shape: str = None,
    mask_shape: str = None
) -> Image.Image:
    """
    Composite a character image onto a portal background.

    Args:
        character_source: URL, file path, or PIL Image of character
        fill: PortalGradient for gradient fill, or path/Image for image fill
        config: AvatarConfig for customization
        portal_shape: Path to portal shape file (PNG or SVG)
        mask_shape: Path to mask shape file (PNG or SVG)

    Returns:
        RGBA image of the complete avatar
    """
    if config is None:
        config = AvatarConfig()

    if fill is None:
        fill = PortalGradient.orange()

    if portal_shape is None:
        portal_shape = os.path.join(SCRIPT_DIR, "portal_shape.png")
    if mask_shape is None:
        mask_shape = os.path.join(SCRIPT_DIR, "mask_shape.png")

    # Create the base canvas
    canvas = Image.new("RGBA", config.output_size, (0, 0, 0, 0))

    # 1. Create portal with fill (gradient or image)
    portal_img = create_portal_with_fill(portal_shape, config.portal_size, fill)

    # Paste portal onto canvas
    canvas.paste(portal_img, config.portal_offset, portal_img)

    # 2. Load and prepare character image
    character = load_character_image(character_source)

    # Scale character using "cover" logic
    target_width, target_height = config.character_size
    img_width, img_height = character.size

    scale = max(target_width / img_width, target_height / img_height)
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    character = character.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Crop to target size
    face_position = getattr(config, 'face_position', 0.0)
    left = (new_width - target_width) // 2
    max_top = new_height - target_height
    top = int(max_top * face_position)
    character = character.crop((left, top, left + target_width, top + target_height))

    # Apply rotation if specified
    if hasattr(config, 'character_rotation') and config.character_rotation != 0:
        character = character.rotate(
            config.character_rotation,
            expand=True,
            resample=Image.Resampling.BICUBIC
        )

    # 3. Load mask shape
    mask = load_shape_mask(mask_shape, config.mask_size)

    # 4. Create expanded work area for negative offsets
    expand_left = abs(min(0, config.mask_offset[0], config.character_offset[0]))
    expand_top = abs(min(0, config.mask_offset[1], config.character_offset[1]))
    expanded_size = (
        config.output_size[0] + expand_left * 2 + 200,
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

    # Create character on expanded canvas
    temp = Image.new("RGBA", expanded_size, (0, 0, 0, 0))
    temp.paste(character, (char_x, char_y))

    # Get character's original alpha
    char_orig_alpha = temp.getchannel("A")

    # Combine character alpha with mask
    final_alpha = ImageChops.multiply(char_orig_alpha, full_mask)

    # Apply combined alpha
    char_expanded = temp.copy()
    char_expanded.putalpha(final_alpha)

    # Crop back to output size
    crop_box = (expand_left, expand_top,
                expand_left + config.output_size[0],
                expand_top + config.output_size[1])
    char_layer = char_expanded.crop(crop_box)

    # 5. Composite masked character onto canvas
    canvas = Image.alpha_composite(canvas, char_layer)

    return canvas


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python avatar_compositor.py <character_image> [output_path] [--fill image.png]")
        print("\nExamples:")
        print("  python avatar_compositor.py character.png avatar.png")
        print("  python avatar_compositor.py character.png avatar.png --fill background.png")
        sys.exit(1)

    character_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "avatar_output.png"

    # Check for --fill argument
    fill = PortalGradient.orange()
    if '--fill' in sys.argv:
        fill_idx = sys.argv.index('--fill')
        if fill_idx + 1 < len(sys.argv):
            fill = sys.argv[fill_idx + 1]

    # Create avatar
    avatar = composite_avatar(character_source=character_path, fill=fill)
    avatar.save(output_path, "PNG")
    print(f"Avatar saved to {output_path}")

    # Create gradient variants
    for name, gradient in [
        ("blue", PortalGradient.blue()),
        ("green", PortalGradient.green()),
        ("purple", PortalGradient.purple()),
    ]:
        variant = composite_avatar(character_source=character_path, fill=gradient)
        variant_path = output_path.replace(".png", f"_{name}.png")
        variant.save(variant_path, "PNG")
        print(f"Variant saved to {variant_path}")
