import SwiftUI

/// The letters of a vertical neon sign, stacked top to bottom.
struct NeonLetters: View {
    let text: String
    let color: Color

    var body: some View {
        VStack(spacing: 0) {
            ForEach(Array(text.enumerated()), id: \.offset) { _, character in
                Text(String(character))
                    .font(.custom("AppleSDGothicNeo-Bold", size: 12))
                    .foregroundStyle(color)
                    .frame(width: 21, height: NeonPlacement.cell)
            }
        }
    }
}
