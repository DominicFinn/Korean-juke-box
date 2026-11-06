import SwiftUI

/// The buildings themselves, drawn once rather than every frame.
struct SkylineBlocks: View {
    let layout: SceneLayout

    var body: some View {
        Canvas { context, _ in
            Skyline.drawBlocks(&context, layout: layout)
        }
        .allowsHitTesting(false)
    }
}
