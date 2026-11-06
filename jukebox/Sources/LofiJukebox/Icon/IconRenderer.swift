import ImageIO
import SwiftUI
import UniformTypeIdentifiers

enum IconRenderer {
    @MainActor
    static func render(to url: URL) {
        let renderer = ImageRenderer(content: AppIconView())
        renderer.scale = 1
        guard let image = renderer.cgImage,
              let destination = CGImageDestinationCreateWithURL(url as CFURL, UTType.png.identifier as CFString, 1, nil) else {
            fatalError("Couldn't render the app icon to \(url.path)")
        }
        CGImageDestinationAddImage(destination, image, nil)
        guard CGImageDestinationFinalize(destination) else {
            fatalError("Couldn't write the app icon to \(url.path)")
        }
    }
}
