import SwiftUI

/// The Playback menu, with keyboard shortcuts.
struct PlaybackCommands: Commands {
    let player: Player

    var body: some Commands {
        CommandMenu("재생") {
            Button("재생/일시정지", action: player.togglePlay)
                .keyboardShortcut(.space, modifiers: [])
            Button("다음 테이프", action: player.skipForward)
                .keyboardShortcut(.rightArrow, modifiers: .command)
            Button("이전 테이프", action: player.skipBack)
                .keyboardShortcut(.leftArrow, modifiers: .command)
        }
    }
}
