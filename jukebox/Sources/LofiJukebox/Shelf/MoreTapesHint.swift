import SwiftUI

/// Shown at the foot of the shelf while there are tapes scrolled out of sight: the list
/// fades out, and a button takes you down to the rest.
struct MoreTapesHint: View {
    let isShowing: Bool
    let showMore: () -> Void

    var body: some View {
        VStack(spacing: 0) {
            LinearGradient(colors: [Palette.paper.opacity(0), Palette.paper], startPoint: .top, endPoint: .bottom)
                .frame(height: 44)
                .allowsHitTesting(false)
            Button(action: showMore) {
                Label("테이프 더 보기", systemImage: "chevron.down")
                    .font(.label(12, relativeTo: .caption))
            }
            .buttonStyle(StickerButtonStyle(fill: Palette.yuzu))
            .padding(.bottom, 8)
            .frame(maxWidth: .infinity)
            .background(Palette.paper)
            .accessibilityLabel("Show more tapes")
        }
        .opacity(isShowing ? 1 : 0)
        .allowsHitTesting(isShowing)
        .accessibilityHidden(!isShowing)
        .animation(.easeOut(duration: 0.2), value: isShowing)
    }
}
