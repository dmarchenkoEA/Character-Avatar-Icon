# Character Avatar Icon (iOS)

A SwiftUI component for compositing character images onto a portal background with automatic head-based framing.

## Features

- **Auto-framing** - Automatically positions and scales characters based on head bounding box
- **Pre-masked support** - Simple path for server-processed images
- **Gradient fills** - Built-in gradients (orange, blue, green, purple, red) or custom colors
- **Image fills** - Use any image as the portal background
- **Responsive** - Scales to fit any frame size while maintaining aspect ratio
- **Matches Python implementation** - Same algorithm and output as the server-side Python compositor

## Usage

### Option A: Auto-framing with Bounding Box

For raw character images with head detection data:

```swift
AvatarIcon(
    characterImage: Image("MyCharacter"),
    imageSize: CGSize(width: 1091, height: 1953),
    headBoundingBox: HeadBoundingBox(x1: 407, y1: 105, x2: 686, y2: 510),
    fill: .orange
)
.frame(width: 170, height: 200)
```

### Option B: Pre-masked Image

For server-processed images that are already scaled and positioned:

```swift
AvatarIcon(
    headshotImage: Image("PreProcessedCharacter"),
    fill: .gradient(.blue)
)
.frame(width: 170, height: 200)
```

### Custom Gradients

```swift
AvatarIcon(
    headshotImage: myImage,
    fill: .gradient(.custom(start: Color.red, end: Color.orange))
)
```

### Image Fill

```swift
AvatarIcon(
    headshotImage: myImage,
    fill: .image(Image("BackgroundTexture"))
)
```

## Auto-Framing Algorithm

The auto-framing uses a unified algorithm that works for any character type:

1. **Define frame region** - From head top to shoulders (head bottom + 50% of head height), or to image bottom for "all-head" characters like Kirby
2. **Scale to fit** - Scales so the frame region is 450pt tall
3. **Position** - Places the frame at y=10 from the top

This naturally adapts to different character proportions without classification.

## Configuration

### AutoFrameConfig

| Parameter | Default | Description |
|-----------|---------|-------------|
| `targetFrameHeight` | 450 | Height of the frame region in points |
| `targetFrameTop` | 10 | Y position for top of frame |
| `shoulderExtension` | 0.5 | How far below head to extend (fraction of head height) |

### HeadBoundingBox

Create from corner coordinates:
```swift
HeadBoundingBox(x1: 407, y1: 105, x2: 686, y2: 510)
```

Or from a CGRect:
```swift
HeadBoundingBox(rect: detectedHeadRect)
```

## Components

| Component | Description |
|-----------|-------------|
| `AvatarIcon` | Main SwiftUI view |
| `AvatarFill` | Enum for gradient or image fills |
| `AvatarGradient` | Predefined and custom gradient colors |
| `HeadBoundingBox` | Head bounding box for auto-framing |
| `AutoFrameConfig` | Configuration for auto-framing parameters |
| `PortalShape` | SwiftUI Shape for the egg-shaped portal |
| `MaskShape` | SwiftUI Shape for character clipping |

## Coordinate System

- Base canvas size: 340×400 points
- Portal size: 340×340 points at offset (0, 60)
- Mask size: 340×430 points at offset (0, -29)
- All sizes scale proportionally based on the frame you provide

## Sample Characters

The demo includes sample characters with pre-computed head bounding boxes:

| Character | Image Size | Head BBox |
|-----------|------------|-----------|
| Fox | 1536×2752 | (586, 21) → (1014, 547) |
| Kirby | 1439×1333 | (92, 1) → (1286, 1197) |
| Frankie | 1091×1953 | (407, 105) → (686, 510) |
| Trainer Rex | 960×1440 | (372, 62) → (598, 307) |
