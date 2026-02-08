# Character Avatar Icon Compositor

A Python tool for compositing character images onto a portal background with masking. Generates stylized avatar icons matching a Figma design.

## Features

- Composites character images onto a portal background
- Uses SVG mask shapes for crisp scaling at any resolution
- **Auto-framing** - Automatically positions characters based on head bounding box
- **Gradient fills** - Customizable colors (orange, blue, green, purple, red, or custom)
- **Image fills** - Use any image as the portal background
- Adjustable character scale, rotation, and position
- Output scaling (1x, 2x, etc.) for different resolution needs
- Supports transparent PNGs
- Web UI for interactive tweaking
- CLI for batch processing

## Installation

Requires Python 3.

```bash
# Dependencies are auto-installed when you run the scripts
./run.sh --help
```

## Usage

### Auto-Framing (Recommended)

The auto-framing feature uses head bounding boxes (from a vision model) to automatically position and scale characters. This works for any character type - from humanoids to characters like Kirby.

```python
from avatar_compositor import composite_avatar, compute_auto_config, PortalGradient
from PIL import Image

# Load character and get head bounding box (from vision model)
img = Image.open("character.png")
head_bbox = [x1, y1, x2, y2]  # Bounding box coordinates

# Compute optimal config based on head position
config = compute_auto_config(img.size, head_bbox)

# Generate avatar
avatar = composite_avatar("character.png", PortalGradient.orange(), config=config)
avatar.save("avatar.png")
```

#### How Auto-Framing Works

1. Takes the head bounding box from a vision model query (e.g., "head")
2. Defines a "frame region" from head top to shoulders (or image bottom for all-head characters)
3. Scales so this frame fits the target area (450px default)
4. Positions the frame at the top of the portal

This unified algorithm naturally adapts to any character type without classification.

#### Auto-Framing Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `target_frame_height` | 450 | Height of the frame region in output pixels |
| `target_frame_top` | 10 | Y position for top of frame in output |
| `shoulder_extension` | 0.5 | How far below head to extend (as fraction of head height) |
| `output_scale` | 1.0 | Scale factor for final output |

### Command Line

```bash
# Basic usage (gradient fill)
./run.sh character.png output.png

# With image fill
./run.sh character.png output.png --fill background.png

# With output scaling (2x resolution)
./run.sh character.png output.png --scale 2.0
```

This generates the avatar with the default orange gradient, plus blue, green, and purple variants.

### Web UI

```bash
./run_ui.sh
```

Opens a Gradio web interface at http://localhost:7860 where you can:
- Upload a character image (transparent PNG recommended)
- Choose between gradient or image fill
- Pick gradient colors with color pickers
- Upload a background image for image fill
- Adjust character scale, rotation, and position
- Set output scale (0.5x to 4x)
- See live preview as you change settings

## Project Structure

```
├── avatar_compositor.py  # Core compositing logic + auto-framing
├── ui.py                 # Gradio web UI
├── run.sh               # CLI entry point
├── run_ui.sh            # Web UI entry point
├── portal_shape.svg     # Portal shape (egg-shaped)
├── mask_shape.svg       # Character clipping mask
├── bounding-boxes.json  # Sample head bounding boxes
├── Sample Characters/   # Example character images
└── requirements.txt     # Python dependencies
```

## How It Works

1. **Portal Layer**: Creates the portal shape with either gradient or image fill
2. **Character Layer**: Loads, scales, and positions the character image
3. **Masking**: Applies the SVG mask shape to clip the character
4. **Compositing**: Layers the masked character over the portal
5. **Sub-pixel rendering**: Uses 2x internal rendering for precise alignment

## Fill Types

### Gradient Fill
```python
from avatar_compositor import composite_avatar, PortalGradient

# Built-in gradients
avatar = composite_avatar("character.png", PortalGradient.orange())
avatar = composite_avatar("character.png", PortalGradient.blue())
avatar = composite_avatar("character.png", PortalGradient.green())
avatar = composite_avatar("character.png", PortalGradient.purple())
avatar = composite_avatar("character.png", PortalGradient.red())

# Custom gradient
custom = PortalGradient(start_color="#FF0000", end_color="#0000FF")
avatar = composite_avatar("character.png", custom)
```

### Image Fill
```python
from avatar_compositor import composite_avatar

# From file path
avatar = composite_avatar("character.png", "landscape.png")

# From URL
avatar = composite_avatar("character.png", "https://example.com/bg.png")
```

## Bounding Box Format

Head bounding boxes should be in `[x1, y1, x2, y2]` format:
- `x1, y1`: Top-left corner of head
- `x2, y2`: Bottom-right corner of head

Example `bounding-boxes.json`:
```json
{
  "character_name": {
    "bbox": [407, 105, 686, 510],
    "label": "head",
    "confidence": 0.67
  }
}
```

## Dependencies

- Pillow - Image processing
- requests - URL fetching
- cairosvg - SVG rendering
- gradio - Web UI (for run_ui.sh only)
