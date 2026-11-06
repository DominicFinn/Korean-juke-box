import SwiftUI

/// The cassette's window: two hubs turning while it plays, with tape winding from the
/// left reel to the right as the tape works through its plays.
struct TapeWindow: View {
    let frame: PlaybackFrame
    /// The deck turns its hubs with Core Animation instead; the icon draws them here
    var showsHubs = true

    var body: some View {
        Canvas { context, size in
            let window = Path(roundedRect: CGRect(origin: .zero, size: size), cornerRadius: 10)
            context.fill(window, with: .color(Palette.smoke))
            context.clip(to: window)

            let left = CGPoint(x: size.width * 0.25, y: size.height / 2)
            let right = CGPoint(x: size.width * 0.75, y: size.height / 2)
            let smallest = 14.0
            let largest = 27.0
            let leftRadius = smallest + (largest - smallest) * (1 - frame.progress)
            let rightRadius = smallest + (largest - smallest) * frame.progress

            for (centre, radius) in [(left, leftRadius), (right, rightRadius)] {
                context.fill(Path(ellipseIn: circle(centre, radius)), with: .color(Palette.tapeBrown))
            }
            var strip = Path()
            strip.move(to: CGPoint(x: left.x, y: left.y + leftRadius))
            strip.addLine(to: CGPoint(x: right.x, y: right.y + rightRadius))
            context.stroke(strip, with: .color(Palette.tapeBrown), lineWidth: 2)

            let spin = Angle.radians(frame.elapsed * 0.7 * 2 * .pi)
            if showsHubs {
                hub(&context, at: left, spin: spin)
                hub(&context, at: right, spin: spin)
            }

            var glint = Path()
            glint.move(to: CGPoint(x: size.width * 0.42, y: size.height - 6))
            glint.addLine(to: CGPoint(x: size.width * 0.52, y: 6))
            context.stroke(glint, with: .color(.white.opacity(0.18)), style: StrokeStyle(lineWidth: 4, lineCap: .round))
        }
        .overlay {
            RoundedRectangle(cornerRadius: 10).strokeBorder(Palette.ink, lineWidth: 2.5)
        }
    }

    private func circle(_ centre: CGPoint, _ radius: Double) -> CGRect {
        CGRect(x: centre.x - radius, y: centre.y - radius, width: radius * 2, height: radius * 2)
    }

    private func hub(_ context: inout GraphicsContext, at centre: CGPoint, spin: Angle) {
        context.fill(Path(ellipseIn: circle(centre, 11)), with: .color(Palette.paperWhite))
        context.stroke(Path(ellipseIn: circle(centre, 11)), with: .color(Palette.ink), lineWidth: 2)
        var teeth = Path()
        for tooth in 0..<6 {
            let angle = spin.radians + Double(tooth) * .pi / 3
            teeth.move(to: CGPoint(x: centre.x + cos(angle) * 4, y: centre.y + sin(angle) * 4))
            teeth.addLine(to: CGPoint(x: centre.x + cos(angle) * 8.5, y: centre.y + sin(angle) * 8.5))
        }
        context.stroke(teeth, with: .color(Palette.ink), style: StrokeStyle(lineWidth: 2.5, lineCap: .round))
    }
}
