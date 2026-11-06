import SwiftUI

/// The wooden window we're looking out of, with a manga glint on each pane, and the sill.
struct WindowFrame: View {
    let layout: SceneLayout

    var body: some View {
        Canvas { context, size in
            let edge = layout.frameWidth
            let glass = CGRect(x: edge, y: edge, width: size.width - edge * 2, height: layout.sillTop - edge)

            var frame = Path(CGRect(origin: .zero, size: size))
            frame.addRect(glass)
            context.fill(frame, with: .color(Palette.wood), style: FillStyle(eoFill: true))
            context.stroke(Path(glass), with: .color(Palette.ink), lineWidth: 2.5)

            let mullion = CGRect(x: layout.mullionX - 5, y: glass.minY, width: 10, height: glass.height)
            context.fill(Path(mullion), with: .color(Palette.wood))
            context.stroke(Path(mullion), with: .color(Palette.ink), lineWidth: 2)

            for paneX in [glass.minX, layout.mullionX + 5] {
                var glint = Path()
                glint.move(to: CGPoint(x: paneX + 22, y: glass.minY + 62))
                glint.addLine(to: CGPoint(x: paneX + 62, y: glass.minY + 22))
                glint.move(to: CGPoint(x: paneX + 26, y: glass.minY + 80))
                glint.addLine(to: CGPoint(x: paneX + 80, y: glass.minY + 26))
                context.stroke(glint, with: .color(.white.opacity(0.22)), style: StrokeStyle(lineWidth: 3, lineCap: .round))
            }

            let top = CGRect(x: 0, y: layout.sillTop, width: size.width, height: 12)
            let front = CGRect(x: 0, y: top.maxY, width: size.width, height: size.height - top.maxY)
            context.fill(Path(front), with: .color(Palette.woodDark))
            context.fill(Path(top), with: .color(Palette.woodLight))
            var edges = Path()
            edges.move(to: CGPoint(x: 0, y: top.minY))
            edges.addLine(to: CGPoint(x: size.width, y: top.minY))
            edges.move(to: CGPoint(x: 0, y: top.maxY))
            edges.addLine(to: CGPoint(x: size.width, y: top.maxY))
            context.stroke(edges, with: .color(Palette.ink), lineWidth: 2.5)
        }
        .allowsHitTesting(false)
    }
}
