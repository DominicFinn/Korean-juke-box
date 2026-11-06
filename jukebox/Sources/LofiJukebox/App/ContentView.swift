import SwiftUI

struct ContentView: View {
    let library: TrackLibrary
    let player: Player

    var body: some View {
        VStack(spacing: 8) {
            TitleBand()
            HStack(spacing: 14) {
                VStack(spacing: 14) {
                    WindowScene(player: player)
                    DeckPanel(player: player)
                        .frame(height: 232)
                }
                ShelfPanel(library: library, player: player)
                    .frame(width: 272)
            }
        }
        .padding(.horizontal, 18)
        .padding(.top, 6)
        .padding(.bottom, 18)
        .frame(minWidth: 960, minHeight: 690)
        .background(PaperBackground())
        .task {
            await library.watch()
        }
        .onChange(of: library.tracks, initial: true) {
            player.setPlaylist(library.tracks)
        }
    }
}
