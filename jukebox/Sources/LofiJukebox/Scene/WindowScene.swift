import SwiftUI

/// The big panel: a rainy night city through the window, with Oreo and Milo, the Finn
/// cats, on the sill.
struct WindowScene: View {
    let player: Player

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        GeometryReader { proxy in
            let layout = SceneLayout(size: proxy.size)
            ZStack(alignment: .topLeading) {
                NightScene(player: player, state: sceneState)
                RainSoundEffect()
                    .position(x: layout.size.width * 0.14, y: layout.size.height * 0.44)
                CatPlaque()
                    .position(x: (layout.oreoX + layout.miloX) / 2, y: layout.sillTop + 29)
                NowPlayingBubble(track: player.current, isPlaying: player.isPlaying)
                    .position(x: layout.oreoX - 62, y: layout.sillTop - 182)
                CaptionBox(text: chapter)
                    .padding(.top, layout.frameWidth + 10)
                    .padding(.leading, layout.frameWidth + 10)
            }
        }
        .mangaPanel()
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(accessibilityDescription)
    }

    private var sceneState: NightSceneView.State {
        let tape = player.current.map { "\($0.id) \($0.modified.timeIntervalSinceReferenceDate)" }
        return NightSceneView.State(tape: tape, isPlaying: player.isPlaying, bpm: player.current?.bpm ?? 0,
                                    reduceMotion: reduceMotion)
    }

    /// "제1화 「심야버스」": episode one, like the opening caption of a webtoon episode.
    private var chapter: String {
        guard let track = player.current, let number = player.currentNumber else { return "제0화 「준비 중」" }
        return "제\(number)화 「\(track.titleKo)」"
    }

    private var accessibilityDescription: String {
        guard let track = player.current else {
            return "Oreo and Milo, the Finn cats, on a windowsill looking out at a rainy city at night"
        }
        return player.isPlaying
            ? "Oreo and Milo, the Finn cats, on the windowsill, bouncing along to \(track.title)"
            : "Oreo and Milo, the Finn cats, dozing on the windowsill. \(track.title) is paused"
    }
}
