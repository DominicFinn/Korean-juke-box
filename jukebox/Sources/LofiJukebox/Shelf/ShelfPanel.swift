import SwiftUI

/// The right-hand panel: every tape, ready to pick.
struct ShelfPanel: View {
    let library: TrackLibrary
    let player: Player

    @State private var isChoosingFolder = false
    @State private var listBottom = 0.0
    @State private var shelfHeight = 0.0

    private nonisolated static let shelfSpace = "shelf"

    /// True while the last tape is still below the bottom of the shelf. The list has
    /// spare padding at the end so the last tape can scroll clear of the hint.
    private var hasMoreBelow: Bool {
        listBottom - 56 > shelfHeight + 4
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ShelfHeader(count: library.tracks.count)
            ScrollViewReader { scroller in
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(Array(library.tracks.enumerated()), id: \.element.id) { index, track in
                            TapeSpine(track: track, number: index + 1, isCurrent: track.id == player.current?.id) {
                                player.play(track)
                            }
                        }
                    }
                    .padding(.leading, 10)
                    .padding(.trailing, 6)
                    .padding(.top, 8)
                    .padding(.bottom, 56)
                    .onGeometryChange(for: Double.self) { proxy in
                        proxy.frame(in: .named(Self.shelfSpace)).maxY
                    } action: { bottom in
                        listBottom = bottom
                    }
                }
                .coordinateSpace(.named(Self.shelfSpace))
                .onGeometryChange(for: Double.self) { proxy in
                    proxy.size.height
                } action: { height in
                    shelfHeight = height
                }
                .overlay(alignment: .bottom) {
                    MoreTapesHint(isShowing: hasMoreBelow) {
                        showMore(using: scroller)
                    }
                }
            }
            .overlay {
                EmptyShelf()
                    .opacity(library.tracks.isEmpty ? 1 : 0)
            }
            ShelfFooter(folder: library.folder, problem: library.problem ?? player.problem, choose: chooseFolder)
        }
        .padding(14)
        .mangaPanel()
        .fileImporter(isPresented: $isChoosingFolder, allowedContentTypes: [.folder]) { result in
            if case .success(let url) = result {
                library.use(folder: url)
            }
        }
    }

    private func showMore(using scroller: ScrollViewProxy) {
        guard let last = library.tracks.last else { return }
        withAnimation(.easeInOut(duration: 0.4)) {
            scroller.scrollTo(last.id, anchor: .bottom)
        }
    }

    private func chooseFolder() {
        isChoosingFolder = true
    }
}
