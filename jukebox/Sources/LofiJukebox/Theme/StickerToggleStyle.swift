import SwiftUI

/// A sticker button that turns pink while it's on.
struct StickerToggleStyle: ToggleStyle {
    func makeBody(configuration: Configuration) -> some View {
        Button {
            configuration.isOn.toggle()
        } label: {
            configuration.label
        }
        .buttonStyle(StickerButtonStyle(fill: configuration.isOn ? Palette.sakura : Palette.paperWhite))
        .accessibilityAddTraits(configuration.isOn ? .isSelected : [])
    }
}
