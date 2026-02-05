# Character Avatar Icon Compositor

A Python tool for compositing character images onto a gradient portal background with SVG masking. Generates stylized avatar icons matching a Figma design.

## Features

- Composites character images onto a gradient portal background
- Uses SVG mask to clip character to a blob shape
- Customizable gradient colors (orange, blue, green, purple, red, or custom)
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
# Basic usage
./run.sh character.png output.png

# From URL
./run.sh https://example.com/character.png output.png
```

This generates the avatar with the default orange gradient, plus blue, green, and purple variants.

### Web UI

```bash
./run_ui.sh
```

Opens a Gradio web interface at http://localhost:7860 where you can:
- Upload a character image (transparent PNG recommended)
- Pick gradient colors with color pickers
- Adjust character scale, rotation, and position
- Tweak mask and portal offsets
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
├── portal.svg           # Portal shape (gradient background)
├── mask.svg             # Mask shape (clips character)
├── Frankie.png          # Example character
└── requirements.txt     # Python dependencies
```

## How It Works

1. **Portal Layer**: Renders the portal SVG with customizable gradient colors
2. **Character Layer**: Loads and scales the character image
3. **Masking**: Applies the mask SVG to clip the character to a blob shape
4. **Compositing**: Layers the masked character over the portal

The portal and mask SVGs share the same coordinate system (340×341) ensuring perfect alignment.

## Dependencies

- Pillow - Image processing
- cairosvg - SVG rendering
- requests - URL fetching
- gradio - Web UI (for run_ui.sh only)
