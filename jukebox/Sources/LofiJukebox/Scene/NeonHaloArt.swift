import SwiftUI

/// The soft glow around a neon sign, padded so the blur has room to spread.
struct NeonHaloArt: View {
    static let spread = 18.0

    let placement: NeonPlacement

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 3)
                .stroke(placement.color, lineWidth: 5)
            NeonLetters(text: placement.text, color: placement.color)
        }
        .frame(width: placement.size.width, height: placement.size.height)
        .blur(radius: 6)
        .padding(Self.spread)
    }
}
