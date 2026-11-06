import SwiftUI

/// Chunky ink-outlined buttons with a hard shadow, which press down when clicked.
struct StickerButtonStyle: ButtonStyle {
    var fill = Palette.paperWhite
    /// Set for round icon buttons; leave nil to size to the label with some padding
    var diameter: CGFloat?
    /// Large values give a capsule or circle, because the radius is capped at half the height
    var cornerRadius = 100.0

    @Environment(\.isEnabled) private var isEnabled

    func makeBody(configuration: Configuration) -> some View {
        let depth = configuration.isPressed ? 1.0 : 3.5
        let shape = RoundedRectangle(cornerRadius: cornerRadius, style: .circular)
        configuration.label
            .foregroundStyle(Palette.ink)
            .lineLimit(1)
            .padding(.horizontal, diameter == nil ? 12 : 0)
            .padding(.vertical, diameter == nil ? 6 : 0)
            .frame(width: diameter, height: diameter)
            .background {
                ZStack {
                    shape.fill(Palette.ink).offset(x: depth, y: depth)
                    shape.fill(fill)
                    shape.strokeBorder(Palette.ink, lineWidth: 2.5)
                }
            }
            .offset(x: 3.5 - depth, y: 3.5 - depth)
            .opacity(isEnabled ? 1 : 0.45)
            .animation(.snappy(duration: 0.12), value: configuration.isPressed)
    }
}
