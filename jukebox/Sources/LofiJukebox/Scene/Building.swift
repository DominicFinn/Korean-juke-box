import CoreGraphics

/// One block in the skyline.
struct Building {
    var rect: CGRect
    var seed: UInt64
    var hasTank: Bool
    var hasAntenna: Bool
}
