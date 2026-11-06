import SwiftUI

struct VolumeControl: View {
    @Bindable var player: Player

    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: "speaker.fill")
                .accessibilityHidden(true)
            Slider(value: $player.volume, in: 0...1) {
                Text("Volume")
            }
            .labelsHidden()
            .tint(Palette.sakuraDeep)
            .frame(width: 150)
            Image(systemName: "speaker.wave.3.fill")
                .accessibilityHidden(true)
        }
        .font(.system(size: 11, weight: .bold))
        .foregroundStyle(Palette.ink)
    }
}
