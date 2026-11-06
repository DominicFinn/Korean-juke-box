import SwiftUI

/// Where a neon sign hangs, and how dim its glow is allowed to get.
struct NeonPlacement {
    /// Height of each letter on the sign
    static let cell = 15.0

    let text: String
    let color: Color
    let origin: CGPoint
    let floor: Double

    var size: CGSize {
        CGSize(width: 21, height: Double(text.count) * Self.cell + 9)
    }
}
