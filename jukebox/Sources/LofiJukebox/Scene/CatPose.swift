import SwiftUI

/// Oreo and Milo, the cats from Seoul Sisters.
enum CatPose: String {
    case oreoBack = "oreo-back"
    case miloBack = "milo-back"
    case oreoLoaf = "oreo-loaf"
    case miloCurl = "milo-curl"
    case oreoHappy = "oreo-happy"

    /// The built app keeps the art in Contents/Resources. `swift run` finds it in the
    /// build folder instead, which is where SwiftPM's own lookup goes.
    private static let resources: Bundle = {
        let name = "LofiJukebox_LofiJukebox.bundle"
        if let url = Bundle.main.resourceURL?.appending(path: name), let bundle = Bundle(url: url) {
            return bundle
        }
        return .module
    }()

    @MainActor private static var cache: [CatPose: NSImage] = [:]

    @MainActor var image: Image {
        Image(nsImage: picture)
    }

    @MainActor var cgImage: CGImage? {
        picture.cgImage(forProposedRect: nil, context: nil, hints: nil)
    }

    @MainActor private var picture: NSImage {
        if let cached = Self.cache[self] {
            return cached
        }
        let loaded = Self.resources.url(forResource: rawValue, withExtension: "webp")
            .flatMap(NSImage.init(contentsOf:)) ?? NSImage()
        Self.cache[self] = loaded
        return loaded
    }
}
