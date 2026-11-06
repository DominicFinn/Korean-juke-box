import SwiftUI

/// The square narration box manga uses for captions.
struct CaptionBox: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.serif(13, relativeTo: .caption))
            .foregroundStyle(Palette.ink)
            .lineLimit(1)
            .padding(.horizontal, 10)
            .padding(.vertical, 5)
            .background(Palette.paperWhite)
            .overlay { Rectangle().strokeBorder(Palette.ink, lineWidth: 2) }
    }
}
