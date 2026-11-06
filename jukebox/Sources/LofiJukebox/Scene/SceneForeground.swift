import SwiftUI

/// The window frame, the sill and the mug: in front of the rain, behind the cats.
struct SceneForeground: View {
    let layout: SceneLayout

    var body: some View {
        ZStack(alignment: .topLeading) {
            WindowFrame(layout: layout)
            MugArt(layout: layout)
        }
        .frame(width: layout.size.width, height: layout.size.height)
    }
}
