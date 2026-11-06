import SwiftUI

struct PlayModeControls: View {
    @Bindable var player: Player

    var body: some View {
        HStack(spacing: 10) {
            Toggle(isOn: $player.shuffle) {
                Label("셔플", systemImage: "shuffle")
            }
            .accessibilityLabel("Shuffle")
            Toggle(isOn: $player.repeatOne) {
                Label("반복", systemImage: "repeat.1")
            }
            .accessibilityLabel("Loop this tape")
        }
        .fixedSize()
        .toggleStyle(StickerToggleStyle())
        .font(.label(12))
    }
}
