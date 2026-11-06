import SwiftUI

struct Moon: View {
    var body: some View {
        ZStack {
            Circle()
                .fill(RadialGradient(colors: [Palette.moon.opacity(0.4), .clear],
                                     center: .center, startRadius: 8, endRadius: 70))
                .frame(width: 140, height: 140)
            CrescentShape()
                .fill(Palette.moon)
                .overlay { CrescentShape().stroke(Palette.ink, lineWidth: 2.5) }
                .frame(width: 46, height: 46)
        }
        .accessibilityHidden(true)
    }
}
