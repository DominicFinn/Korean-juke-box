import SwiftUI

/// A mug of tea on the sill. The steam is animated separately.
struct MugArt: View {
    let layout: SceneLayout

    var body: some View {
        Canvas { context, _ in
            let x = layout.mugX
            let base = layout.sillTop + 3
            let cup = Path(roundedRect: CGRect(x: x - 16, y: base - 34, width: 32, height: 34),
                           cornerRadii: RectangleCornerRadii(bottomLeading: 8, bottomTrailing: 8))
            var handle = Path()
            handle.addArc(center: CGPoint(x: x + 16, y: base - 18), radius: 8,
                          startAngle: .degrees(-70), endAngle: .degrees(70), clockwise: false)
            context.stroke(handle, with: .color(Palette.ink), lineWidth: 5)
            context.fill(cup, with: .color(Palette.paperWhite))
            context.fill(Path(CGRect(x: x - 16, y: base - 25, width: 32, height: 7)), with: .color(Palette.sakura))
            context.stroke(cup, with: .color(Palette.ink), lineWidth: 2.5)
            context.draw(Text("차").font(.custom("AppleMyungjo", size: 10)).foregroundStyle(Palette.ink),
                         at: CGPoint(x: x, y: base - 9))
        }
    }
}
