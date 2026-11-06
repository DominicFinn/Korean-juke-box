import SwiftUI

/// A name label stuck to the front of the sill: "the Finns' cats, Oreo and Milo".
struct CatPlaque: View {
    var body: some View {
        Text("핀네 고양이들 · 오레오와 마일로")
            .font(.serif(12, relativeTo: .caption))
            .foregroundStyle(Palette.ink)
            .lineLimit(1)
            .fixedSize()
            .padding(.horizontal, 10)
            .padding(.vertical, 4)
            .background(Palette.paperWhite)
            .overlay { Rectangle().strokeBorder(Palette.ink, lineWidth: 1.5) }
            .rotationEffect(.degrees(-1.5))
            .accessibilityHidden(true)
    }
}
