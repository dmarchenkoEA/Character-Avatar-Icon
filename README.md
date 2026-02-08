# Character Avatar Icon Compositor

A Python tool for compositing character images onto a portal background with masking. Generates stylized avatar icons matching a Figma design.

## Features

- Composites character images onto a portal background
- Uses PNG mask to clip character to an egg-shaped blob
- **Gradient fills** - Customizable colors (orange, blue, green, purple, red, or custom)
- **Image fills** - Use any image as the portal background
- Adjustable character scale, rotation, and position
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

### Command Line

```bash
# Basic usage (gradient fill)
./run.sh character.png output.png

# With image fill
./run.sh character.png output.png --fill background.png
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
- See live preview as you change settings

## Configuration

Default settings (can be adjusted in UI or code):

| Setting | Default | Description |
|---------|---------|-------------|
| Character Scale | 1.1 | Size multiplier for character |
| Rotation | 3° | Counter-clockwise rotation |
| X Offset | -70 | Horizontal position adjustment |
| Y Offset | -40 | Vertical position adjustment |

## Project Structure

```
├── avatar_compositor.py  # Core compositing logic
├── ui.py                 # Gradio web UI
├── run.sh               # CLI entry point
├── run_ui.sh            # Web UI entry point
├── portal_shape.png     # Portal shape mask (egg-shaped)
├── mask_shape.png       # Character mask shape
├── Frankie.png          # Example character
└── requirements.txt     # Python dependencies
```

## How It Works

1. **Portal Layer**: Creates the portal shape with either gradient or image fill
2. **Character Layer**: Loads and scales the character image
3. **Masking**: Applies the mask shape to clip the character
4. **Compositing**: Layers the masked character over the portal

## Fill Types

### Gradient Fill
```python
from avatar_compositor import composite_avatar, PortalGradient

avatar = composite_avatar("character.png", PortalGradient.blue())
```

### Image Fill
```python
from avatar_compositor import composite_avatar

avatar = composite_avatar("character.png", "landscape.png")
```

## Dependencies

- Pillow - Image processing
- requests - URL fetching
- gradio - Web UI (for run_ui.sh only)
- cairosvg - SVG rendering (optional, for legacy SVG shapes)
