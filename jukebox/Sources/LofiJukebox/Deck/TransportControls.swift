import SwiftUI

struct TransportControls: View {
    let player: Player

    var body: some View {
        HStack(spacing: 14) {
            Button("Previous tape", systemImage: "backward.fill", action: player.skipBack)
                .buttonStyle(StickerButtonStyle(diameter: 42))
            Button(player.isPlaying ? "Pause" : "Play",
                   systemImage: player.isPlaying ? "pause.fill" : "play.fill",
                   action: player.togglePlay)
                .buttonStyle(StickerButtonStyle(fill: Palette.sakura, diameter: 56))
                .font(.system(size: 22, weight: .heavy))
            Button("Next tape", systemImage: "forward.fill", action: player.skipForward)
                .buttonStyle(StickerButtonStyle(diameter: 42))
        }
        .labelStyle(.iconOnly)
        .font(.system(size: 15, weight: .heavy))
        .disabled(player.playlist.isEmpty)
    }
}
