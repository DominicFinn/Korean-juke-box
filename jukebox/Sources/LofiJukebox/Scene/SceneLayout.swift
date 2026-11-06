import CoreGraphics

/// Where things sit in the window scene, shared by the drawing layers and the overlays.
struct SceneLayout {
    let size: CGSize

    var frameWidth: Double { 12 }
    var sillHeight: Double { 46 }
    var sillTop: Double { size.height - sillHeight }
    var mullionX: Double { size.width * 0.5 }
    var oreoX: Double { size.width * 0.655 }
    var miloX: Double { size.width * 0.835 }
    /// Where the cats' feet go, a little way into the top of the sill
    var catBase: Double { sillTop + 7 }
    var mugX: Double { size.width * 0.15 }
    var moon: CGPoint { CGPoint(x: size.width * 0.82, y: size.height * 0.2) }

    /// Where the music notes and the sleepy z's float up from, above Milo
    var catHead: CGPoint { CGPoint(x: miloX, y: sillTop - 104) }
}
