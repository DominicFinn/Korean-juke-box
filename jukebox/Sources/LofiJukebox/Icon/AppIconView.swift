import SwiftUI

/// The app icon: a pink tape under the moon, with Oreo peeking over the top.
struct AppIconView: View {
    private static let sample = Track(
        id: "icon", url: URL(filePath: "/"), title: "Lofi Tape", titleKo: "로파이", style: "",
        bpm: 0, key: "", seconds: 30, modified: .distantPast
    )

    var body: some View {
        let shape = RoundedRectangle(cornerRadius: 185, style: .continuous)
        ZStack {
            shape.fill(LinearGradient(colors: [Palette.night, Palette.dusk, Palette.horizon],
                                      startPoint: .top, endPoint: .bottom))
            Screentone(color: Palette.ink.opacity(0.3), spacing: 22, maxRadius: 7, top: 1, bottom: -0.4)
            Moon()
                .scaleEffect(3)
                .position(x: 175, y: 175)
            CatPose.oreoHappy.image
                .resizable()
                .scaledToFit()
                .frame(height: 430)
                .position(x: 470, y: 330)
            CassetteView(track: Self.sample) {
                TapeWindow(frame: PlaybackFrame(elapsed: 0.15, loopSeconds: 30, plays: 2))
            }
                .scaleEffect(2.35)
                .rotationEffect(.degrees(-7))
                .position(x: 412, y: 505)
            shape.strokeBorder(Palette.ink, lineWidth: 20)
        }
        .clipShape(shape)
        .frame(width: 824, height: 824)
        .frame(width: 1024, height: 1024)
    }
}
