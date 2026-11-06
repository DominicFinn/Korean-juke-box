import SwiftUI

/// The page the panels are printed on.
struct PaperBackground: View {
    var body: some View {
        ZStack(alignment: .bottomLeading) {
            Palette.paper
            Screentone(color: Palette.paperShade, spacing: 8, maxRadius: 2.4, top: -1, bottom: 1)
                .frame(width: 260, height: 220)
        }
        .ignoresSafeArea()
    }
}
