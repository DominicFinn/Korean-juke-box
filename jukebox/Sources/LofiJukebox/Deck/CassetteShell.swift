import SwiftUI

/// The plastic parts of the cassette: screws and the bottom ridge with its holes.
struct CassetteShell: View {
    var body: some View {
        Canvas { context, size in
            let screws = [CGPoint(x: 13, y: 13), CGPoint(x: size.width - 13, y: 13),
                          CGPoint(x: 13, y: size.height - 13), CGPoint(x: size.width - 13, y: size.height - 13),
                          CGPoint(x: size.width / 2, y: size.height - 13)]
            for screw in screws {
                let head = Path(ellipseIn: CGRect(x: screw.x - 4.5, y: screw.y - 4.5, width: 9, height: 9))
                context.fill(head, with: .color(Palette.paperShade))
                context.stroke(head, with: .color(Palette.ink), lineWidth: 1.5)
                var slot = Path()
                slot.move(to: CGPoint(x: screw.x - 2.5, y: screw.y - 2.5))
                slot.addLine(to: CGPoint(x: screw.x + 2.5, y: screw.y + 2.5))
                context.stroke(slot, with: .color(Palette.ink), lineWidth: 1.2)
            }

            let ridgeTop = size.height - 32
            var ridge = Path()
            ridge.move(to: CGPoint(x: size.width * 0.2, y: ridgeTop))
            ridge.addLine(to: CGPoint(x: size.width * 0.8, y: ridgeTop))
            ridge.addLine(to: CGPoint(x: size.width * 0.86, y: size.height - 1.5))
            ridge.addLine(to: CGPoint(x: size.width * 0.14, y: size.height - 1.5))
            ridge.closeSubpath()
            context.fill(ridge, with: .color(.black.opacity(0.12)))
            context.stroke(ridge, with: .color(Palette.ink), lineWidth: 2)

            for fraction in [0.3, 0.7] {
                let hole = CGRect(x: size.width * fraction - 5, y: ridgeTop + 9, width: 10, height: 10)
                context.fill(Path(ellipseIn: hole), with: .color(Palette.ink))
            }
            for fraction in [0.42, 0.58] {
                let hole = CGRect(x: size.width * fraction - 4, y: ridgeTop + 11, width: 8, height: 7)
                context.fill(Path(hole), with: .color(Palette.ink))
            }
        }
        .allowsHitTesting(false)
    }
}
