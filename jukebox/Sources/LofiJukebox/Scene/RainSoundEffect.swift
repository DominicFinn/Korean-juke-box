import SwiftUI

/// Comic sound-effect lettering for the rain: 쏴아아, "sswaaa".
struct RainSoundEffect: View {
    var body: some View {
        ZStack {
            Text("쏴아아…")
                .foregroundStyle(Palette.ink)
                .offset(x: 2, y: 2)
            Text("쏴아아…")
                .foregroundStyle(Palette.paperWhite)
        }
        .font(.heavy(26))
        .rotationEffect(.degrees(-10))
        .opacity(0.8)
        .accessibilityHidden(true)
    }
}
