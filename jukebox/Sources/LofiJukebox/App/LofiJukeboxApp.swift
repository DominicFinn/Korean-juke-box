import SwiftUI

struct LofiJukeboxApp: App {
    @State private var library = TrackLibrary()
    @State private var player = Player()

    init() {
        DebugSnapshot.scheduleIfRequested()
    }

    var body: some Scene {
        Window("아빠의 멋진 로파이 앱", id: "jukebox") {
            ContentView(library: library, player: player)
                .preferredColorScheme(.light)
        }
        .windowStyle(.hiddenTitleBar)
        .windowResizability(.contentMinSize)
        .defaultSize(width: 960, height: 690)
        .commands {
            PlaybackCommands(player: player)
        }
    }
}
