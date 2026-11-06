import SwiftUI

/// The bottom panel: the cassette that's in, and the controls. The hubs and the level
/// lights animate themselves; the tape and the readout only need redrawing once a second.
struct DeckPanel: View {
    let player: Player

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        HStack(spacing: 22) {
            CassetteView(track: player.current) {
                TimelineView(.periodic(from: .now, by: 1)) { _ in
                    TapeWindow(frame: player.frame(), showsHubs: false)
                }
                .overlay {
                    SpinningHubs(isSpinning: player.isPlaying && !reduceMotion)
                }
            }
            VStack(alignment: .leading, spacing: 11) {
                TransportControls(player: player)
                PlayModeControls(player: player)
                PlaysControl(player: player)
                HStack(spacing: 12) {
                    LevelLights(player: player)
                    TimelineView(.periodic(from: .now, by: 1)) { _ in
                        DeckReadout(frame: player.frame())
                    }
                }
                VolumeControl(player: player)
            }
        }
        .padding(.horizontal, 16)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        .background(alignment: .bottomTrailing) {
            Screentone(color: Palette.sakura.opacity(0.5), spacing: 7, maxRadius: 2.2, top: -0.6, bottom: 1)
                .frame(width: 240)
        }
        .mangaPanel()
    }
}
