import SwiftUI

/// Paints SwiftUI views and small sprites into images for Core Animation layers.
@MainActor
enum SceneArt {
    static func image(_ view: some View, scale: Double) -> CGImage? {
        let renderer = ImageRenderer(content: view)
        renderer.scale = scale
        return renderer.cgImage
    }

    /// A single glyph, such as a music note for the notes drifting up from the cats.
    static func glyph(_ text: String, font: Font, color: Color, scale: Double) -> CGImage? {
        image(Text(text).font(font).foregroundStyle(color).padding(2), scale: scale)
    }

    /// A thin raindrop streak, leaning the way the rain falls.
    static func rainStreak(scale: Double) -> CGImage? {
        let width = Int(8 * scale)
        let height = Int(32 * scale)
        guard let context = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8, bytesPerRow: 0,
                                      space: CGColorSpaceCreateDeviceRGB(),
                                      bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { return nil }
        context.scaleBy(x: scale, y: scale)
        context.setStrokeColor(CGColor(gray: 1, alpha: 1))
        context.setLineWidth(1.4)
        context.setLineCap(.round)
        context.move(to: CGPoint(x: 6.5, y: 31))
        context.addLine(to: CGPoint(x: 1.5, y: 1))
        context.strokePath()
        return context.makeImage()
    }
}
