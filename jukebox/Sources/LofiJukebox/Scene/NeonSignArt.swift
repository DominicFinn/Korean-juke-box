import SwiftUI

/// A vertical neon sign: dark box, coloured tube round the edge, glowing letters.
struct NeonSignArt: View {
    let placement: NeonPlacement

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 3).fill(Palette.ink)
            RoundedRectangle(cornerRadius: 2)
                .stroke(placement.color, lineWidth: 1.2)
                .padding(2)
            NeonLetters(text: placement.text, color: placement.color)
            NeonLetters(text: placement.text, color: Palette.paperWhite)
                .opacity(0.35)
        }
        .frame(width: placement.size.width, height: placement.size.height)
    }
}
