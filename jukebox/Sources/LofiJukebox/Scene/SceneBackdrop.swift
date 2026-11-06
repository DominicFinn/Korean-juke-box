import SwiftUI

/// Everything behind the rain that never moves: sky, moon and buildings. Painted once
/// into an image for the scene's back layer.
struct SceneBackdrop: View {
    let layout: SceneLayout

    var body: some View {
        ZStack(alignment: .topLeading) {
            NightSky(layout: layout)
            SkylineBlocks(layout: layout)
        }
        .frame(width: layout.size.width, height: layout.size.height)
    }
}
