import SwiftUI

/// The cat's speech bubble, saying what's on.
struct NowPlayingBubble: View {
    let track: Track?
    let isPlaying: Bool

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        ZStack {
            bubble
                .id(track?.id)
                .transition(reduceMotion ? .opacity : .scale(scale: 0.6, anchor: .bottomTrailing).combined(with: .opacity))
        }
        .animation(.bouncy(duration: 0.45), value: track?.id)
    }

    private var bubble: some View {
        VStack(spacing: 2) {
            Text(headline)
                .font(.label(17, relativeTo: .headline))
            Text(subline)
                .font(.label(11, relativeTo: .caption))
                .opacity(0.7)
        }
        .foregroundStyle(Palette.ink)
        .lineLimit(1)
        .padding(.horizontal, 18)
        .padding(.top, 10)
        .padding(.bottom, 26)
        .background {
            SpeechBubbleShape(tail: 0.82).fill(Palette.paperWhite)
            SpeechBubbleShape(tail: 0.82).stroke(Palette.ink, lineWidth: 2.5)
        }
        .fixedSize()
    }

    private var headline: String {
        guard let track else { return "테이프가 없다냥…" }
        return isPlaying ? "♪ \(track.titleKo)" : "쿨쿨…"
    }

    private var subline: String {
        guard let track else { return "아직 아무것도 없어요" }
        return isPlaying ? track.title : "일시정지 · \(track.titleKo)"
    }
}
