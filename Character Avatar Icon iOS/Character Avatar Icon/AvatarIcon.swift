//
//  AvatarIcon.swift
//  Character Avatar Icon
//
//  A SwiftUI component for compositing character images onto a portal background.
//

import SwiftUI

// MARK: - AvatarFill

/// Defines the fill type for the portal background
enum AvatarFill {
    case gradient(AvatarGradient)
    case image(Image)

    // Convenience initializers for built-in gradients
    static var orange: AvatarFill { .gradient(.orange) }
    static var blue: AvatarFill { .gradient(.blue) }
    static var green: AvatarFill { .gradient(.green) }
    static var purple: AvatarFill { .gradient(.purple) }
    static var red: AvatarFill { .gradient(.red) }
}

/// Predefined gradient colors for the portal
enum AvatarGradient {
    case orange
    case blue
    case green
    case purple
    case red
    case custom(start: Color, end: Color)

    var colors: (start: Color, end: Color) {
        switch self {
        case .orange:
            return (Color(hex: "CE782D"), Color(hex: "E1A371"))
        case .blue:
            return (Color(hex: "2D7ECE"), Color(hex: "71A3E1"))
        case .green:
            return (Color(hex: "2DCE78"), Color(hex: "71E1A3"))
        case .purple:
            return (Color(hex: "782DCE"), Color(hex: "A371E1"))
        case .red:
            return (Color(hex: "CE2D2D"), Color(hex: "E17171"))
        case .custom(let start, let end):
            return (start, end)
        }
    }

    var linearGradient: LinearGradient {
        LinearGradient(
            colors: [colors.start, colors.end],
            startPoint: .topTrailing,
            endPoint: .bottomLeading
        )
    }
}

// MARK: - HeadBoundingBox

/// Bounding box for a character's head, used for auto-framing
struct HeadBoundingBox {
    let x: CGFloat
    let y: CGFloat
    let width: CGFloat
    let height: CGFloat

    var rect: CGRect {
        CGRect(x: x, y: y, width: width, height: height)
    }

    var centerX: CGFloat { x + width / 2 }
    var centerY: CGFloat { y + height / 2 }

    /// Create from [x1, y1, x2, y2] format
    init(x1: CGFloat, y1: CGFloat, x2: CGFloat, y2: CGFloat) {
        self.x = x1
        self.y = y1
        self.width = x2 - x1
        self.height = y2 - y1
    }

    init(rect: CGRect) {
        self.x = rect.minX
        self.y = rect.minY
        self.width = rect.width
        self.height = rect.height
    }
}

// MARK: - Auto-Framing Configuration

/// Configuration for auto-framing characters based on head bounding box
struct AutoFrameConfig {
    /// Height of the frame region in output pixels
    var targetFrameHeight: CGFloat = 450
    /// Y position for top of frame in output
    var targetFrameTop: CGFloat = 10
    /// How far below head to extend (as fraction of head height)
    var shoulderExtension: CGFloat = 0.5

    static let `default` = AutoFrameConfig()
}

// MARK: - AvatarIcon View

/// A view that composites a character image onto a portal background
struct AvatarIcon: View {
    private let content: AvatarContent
    private let fill: AvatarFill

    /// The base size of the avatar (portal is 340x340, canvas is 340x400)
    private let baseSize = CGSize(width: 340, height: 400)
    private let portalSize = CGSize(width: 340, height: 340)
    private let portalOffset = CGPoint(x: 0, y: 60)

    // MARK: - Initializers

    /// Initialize with a pre-masked headshot image (simple path)
    /// - Parameters:
    ///   - headshotImage: Pre-processed character image, already scaled and positioned
    ///   - fill: The fill type for the portal background
    init(headshotImage: Image, fill: AvatarFill) {
        self.content = .preMasked(headshotImage)
        self.fill = fill
    }

    /// Initialize with a raw character image and head bounding box (auto-framing)
    /// - Parameters:
    ///   - characterImage: Raw character image
    ///   - imageSize: Size of the character image in pixels
    ///   - headBoundingBox: Bounding box of the character's head
    ///   - fill: The fill type for the portal background
    ///   - config: Auto-framing configuration
    init(
        characterImage: Image,
        imageSize: CGSize,
        headBoundingBox: HeadBoundingBox,
        fill: AvatarFill,
        config: AutoFrameConfig = .default
    ) {
        self.content = .autoFrame(
            image: characterImage,
            imageSize: imageSize,
            bbox: headBoundingBox,
            config: config
        )
        self.fill = fill
    }

    // MARK: - Body

    var body: some View {
        GeometryReader { geometry in
            let scale = min(
                geometry.size.width / baseSize.width,
                geometry.size.height / baseSize.height
            )

            ZStack(alignment: .topLeading) {
                // Portal layer with fill
                portalView
                    .offset(
                        x: portalOffset.x * scale,
                        y: portalOffset.y * scale
                    )

                // Character layer
                characterView
            }
            .frame(width: baseSize.width * scale, height: baseSize.height * scale)
            .frame(width: geometry.size.width, height: geometry.size.height)
        }
        .aspectRatio(baseSize.width / baseSize.height, contentMode: .fit)
    }

    // MARK: - Portal View

    @ViewBuilder
    private var portalView: some View {
        GeometryReader { geometry in
            let scale = min(
                geometry.size.width / baseSize.width,
                geometry.size.height / baseSize.height
            )

            switch fill {
            case .gradient(let gradient):
                PortalShape()
                    .fill(gradient.linearGradient)
                    .frame(
                        width: portalSize.width * scale,
                        height: portalSize.height * scale
                    )
            case .image(let image):
                image
                    .resizable()
                    .scaledToFill()
                    .frame(
                        width: portalSize.width * scale,
                        height: portalSize.height * scale
                    )
                    .clipShape(PortalShape())
            }
        }
    }

    // MARK: - Character View

    @ViewBuilder
    private var characterView: some View {
        GeometryReader { geometry in
            let scale = min(
                geometry.size.width / baseSize.width,
                geometry.size.height / baseSize.height
            )

            switch content {
            case .preMasked(let image):
                image
                    .resizable()
                    .scaledToFit()
                    .frame(width: baseSize.width * scale, height: baseSize.height * scale)

            case .autoFrame(let image, let imageSize, let bbox, let config):
                let transform = computeTransform(
                    imageSize: imageSize,
                    bbox: bbox,
                    config: config,
                    scale: scale
                )

                let maskOffsetY: CGFloat = -29.0 * scale
                let maskHeight: CGFloat = 430 * scale
                let maskWidth: CGFloat = 340 * scale

                // Container for clipping
                Color.clear
                    .frame(width: baseSize.width * scale, height: baseSize.height * scale)
                    .overlay(alignment: .topLeading) {
                        image
                            .resizable()
                            .frame(
                                width: transform.size.width,
                                height: transform.size.height
                            )
                            .offset(x: transform.offset.x, y: transform.offset.y)
                    }
                    .clipped()
                    .mask(
                        MaskShape()
                            .frame(width: maskWidth, height: maskHeight)
                            .frame(
                                width: baseSize.width * scale,
                                height: baseSize.height * scale,
                                alignment: .top
                            )
                            .offset(y: maskOffsetY)
                    )
            }
        }
    }

    // MARK: - Auto-Framing Logic

    private struct CharacterTransform {
        let size: CGSize
        let offset: CGPoint
    }

    private func computeTransform(
        imageSize: CGSize,
        bbox: HeadBoundingBox,
        config: AutoFrameConfig,
        scale: CGFloat
    ) -> CharacterTransform {
        // Define the "frame region" from head top to shoulders (or image bottom)
        let frameTop = bbox.y
        let frameBottom = min(
            bbox.y + bbox.height + bbox.height * config.shoulderExtension,
            imageSize.height
        )
        let frameHeight = frameBottom - frameTop
        let frameCenterX = bbox.centerX

        // Scale so the frame fits the target height (in base 340x400 coordinates)
        let imageScale = config.targetFrameHeight / frameHeight

        // Calculate dimensions in base coordinates, then apply view scale
        let baseWidth = imageSize.width * imageScale
        let baseHeight = imageSize.height * imageScale

        // Calculate where the frame top will be after scaling (in base coordinates)
        let baseFrameTop = frameTop * imageScale
        let baseFrameCenterX = frameCenterX * imageScale

        // Calculate offset in base coordinates
        let baseOutputCenterX: CGFloat = 170
        let baseOffsetX = baseOutputCenterX - baseFrameCenterX
        let baseOffsetY = config.targetFrameTop - baseFrameTop

        // Apply view scale to all values
        return CharacterTransform(
            size: CGSize(width: baseWidth * scale, height: baseHeight * scale),
            offset: CGPoint(x: baseOffsetX * scale, y: baseOffsetY * scale)
        )
    }
}

// MARK: - Content Type

private enum AvatarContent {
    case preMasked(Image)
    case autoFrame(image: Image, imageSize: CGSize, bbox: HeadBoundingBox, config: AutoFrameConfig)
}

// MARK: - Portal Shape

/// The egg-shaped portal background
struct PortalShape: Shape {
    func path(in rect: CGRect) -> Path {
        let scaleX = rect.width / 115
        let scaleY = rect.height / 127

        var path = Path()

        // Converted from SVG: M99.5858 7.25803C77.9528 -8.97968...
        path.move(to: CGPoint(x: 99.5858 * scaleX, y: 7.25803 * scaleY))

        path.addCurve(
            to: CGPoint(x: 18.3279 * scaleX, y: 33.9005 * scaleY),
            control1: CGPoint(x: 77.9528 * scaleX, y: -8.97968 * scaleY),
            control2: CGPoint(x: 41.5729 * scaleX, y: 2.94184 * scaleY)
        )

        path.addCurve(
            to: CGPoint(x: 15.4114 * scaleX, y: 119.358 * scaleY),
            control1: CGPoint(x: -4.92144 * scaleX, y: 64.8635 * scaleY),
            control2: CGPoint(x: -6.22582 * scaleX, y: 103.12 * scaleY)
        )

        path.addCurve(
            to: CGPoint(x: 96.6736 * scaleX, y: 92.7151 * scaleY),
            control1: CGPoint(x: 37.0487 * scaleX, y: 135.595 * scaleY),
            control2: CGPoint(x: 73.42 * scaleX, y: 123.674 * scaleY)
        )

        path.addCurve(
            to: CGPoint(x: 99.5901 * scaleX, y: 7.25803 * scaleY),
            control1: CGPoint(x: 119.919 * scaleX, y: 61.7521 * scaleY),
            control2: CGPoint(x: 121.227 * scaleX, y: 23.4957 * scaleY)
        )

        path.addLine(to: CGPoint(x: 99.5858 * scaleX, y: 7.25803 * scaleY))
        path.closeSubpath()

        return path
    }
}

// MARK: - Mask Shape

/// The clipping mask for the character
struct MaskShape: Shape {
    func path(in rect: CGRect) -> Path {
        let scaleX = rect.width / 115
        let scaleY = rect.height / 160

        var path = Path()

        // Converted from SVG: M0.305776 1.99056e-05C0.305776 38.9963...
        path.move(to: CGPoint(x: 0.305776 * scaleX, y: 0 * scaleY))

        path.addCurve(
            to: CGPoint(x: 0.00013736 * scaleX, y: 117 * scaleY),
            control1: CGPoint(x: 0.305776 * scaleX, y: 38.9963 * scaleY),
            control2: CGPoint(x: 0.0814885 * scaleX, y: 78.2055 * scaleY)
        )

        path.addCurve(
            to: CGPoint(x: 15.4114 * scaleX, y: 152.17 * scaleY),
            control1: CGPoint(x: -0.0305194 * scaleX, y: 131.619 * scaleY),
            control2: CGPoint(x: 5.07032 * scaleX, y: 144.409 * scaleY)
        )

        path.addCurve(
            to: CGPoint(x: 96.6736 * scaleX, y: 125.527 * scaleY),
            control1: CGPoint(x: 37.0487 * scaleX, y: 168.408 * scaleY),
            control2: CGPoint(x: 73.42 * scaleX, y: 156.486 * scaleY)
        )

        path.addCurve(
            to: CGPoint(x: 114.921 * scaleX, y: 71.9999 * scaleY),
            control1: CGPoint(x: 109.638 * scaleX, y: 108.259 * scaleY),
            control2: CGPoint(x: 115.779 * scaleX, y: 88.7209 * scaleY)
        )

        path.addCurve(
            to: CGPoint(x: 114.926 * scaleX, y: 0 * scaleY),
            control1: CGPoint(x: 114.921 * scaleX, y: 71.9999 * scaleY),
            control2: CGPoint(x: 114.926 * scaleX, y: 24.0636 * scaleY)
        )

        path.addCurve(
            to: CGPoint(x: 0.305776 * scaleX, y: 0 * scaleY),
            control1: CGPoint(x: 88.9258 * scaleX, y: 0 * scaleY),
            control2: CGPoint(x: 22.3058 * scaleX, y: 0 * scaleY)
        )

        path.closeSubpath()

        return path
    }
}

// MARK: - Color Extension

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - Previews

#Preview("Gradient Fill") {
    VStack(spacing: 20) {
        // Pre-masked example (using SF Symbol as placeholder)
        AvatarIcon(
            headshotImage: Image(systemName: "person.fill"),
            fill: .orange
        )
        .frame(width: 170, height: 200)

        HStack(spacing: 10) {
            AvatarIcon(headshotImage: Image(systemName: "person.fill"), fill: .blue)
                .frame(width: 85, height: 100)
            AvatarIcon(headshotImage: Image(systemName: "person.fill"), fill: .green)
                .frame(width: 85, height: 100)
            AvatarIcon(headshotImage: Image(systemName: "person.fill"), fill: .purple)
                .frame(width: 85, height: 100)
            AvatarIcon(headshotImage: Image(systemName: "person.fill"), fill: .red)
                .frame(width: 85, height: 100)
        }
    }
    .padding()
}
