import SwiftUI

/// A cassette tape in the shell colour of whatever's playing. `reels` fills the window,
/// so only that part needs to redraw while the tape turns.
struct CassetteView<Reels: View>: View {
    let track: Track?
    @ViewBuilder let reels: Reels

    static var size: CGSize { CGSize(width: 300, height: 180) }

    var body: some View {
        ZStack(alignment: .topLeading) {
            RoundedRectangle(cornerRadius: 14).fill(track?.tapeColor ?? Palette.paperShade)
            CassetteShell()
            CassetteLabel(track: track)
                .frame(width: 262, height: 108)
                .offset(x: 19, y: 12)
            reels
                .frame(width: 170, height: 54)
                .offset(x: 65, y: 62)
            RoundedRectangle(cornerRadius: 14).strokeBorder(Palette.ink, lineWidth: 3)
        }
        .frame(width: Self.size.width, height: Self.size.height)
        .accessibilityHidden(true)
    }
}
