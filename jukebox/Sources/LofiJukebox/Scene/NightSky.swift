import SwiftUI

/// The parts of the sky that don't move: dusk gradient, screentone and the moon.
struct NightSky: View {
    let layout: SceneLayout

    var body: some View {
        ZStack(alignment: .topLeading) {
            LinearGradient(colors: [Palette.night, Palette.dusk, Palette.horizon],
                           startPoint: .top, endPoint: .bottom)
            Screentone(color: Palette.ink.opacity(0.32), spacing: 6, maxRadius: 1.9, top: 1, bottom: -0.5)
            Moon()
                .position(layout.moon)
        }
    }
}
