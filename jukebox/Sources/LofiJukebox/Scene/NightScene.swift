import SwiftUI

/// Puts the Core Animation night scene into SwiftUI.
struct NightScene: NSViewRepresentable {
    let player: Player
    let state: NightSceneView.State

    func makeNSView(context: Context) -> NightSceneView {
        let view = NightSceneView()
        view.player = player
        return view
    }

    func updateNSView(_ view: NightSceneView, context: Context) {
        view.update(state)
    }
}
