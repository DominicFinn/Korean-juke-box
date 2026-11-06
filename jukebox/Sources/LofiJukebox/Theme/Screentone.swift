import SwiftUI

/// Halftone dots like manga screentone. Dot size runs from `top` at the top edge to
/// `bottom` at the bottom edge, as a fraction of `maxRadius`; below zero there are no dots.
struct Screentone: View {
    var color: Color
    var spacing = 6.0
    var maxRadius = 1.8
    var top = 1.0
    var bottom = 0.0

    var body: some View {
        Canvas { context, size in
            var dots = Path()
            var row = 0
            for y in stride(from: 0.0, through: size.height, by: spacing) {
                let radius = maxRadius * (top + (bottom - top) * y / max(size.height, 1))
                if radius > 0.2 {
                    let shift = row.isMultiple(of: 2) ? 0 : spacing / 2
                    for x in stride(from: shift, through: size.width, by: spacing) {
                        dots.addEllipse(in: CGRect(x: x - radius, y: y - radius, width: radius * 2, height: radius * 2))
                    }
                }
                row += 1
            }
            context.fill(dots, with: .color(color))
        }
        .allowsHitTesting(false)
        .accessibilityHidden(true)
    }
}
