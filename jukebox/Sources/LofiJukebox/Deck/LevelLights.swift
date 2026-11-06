import SwiftUI

struct LevelLights: NSViewRepresentable {
    let player: Player

    func makeNSView(context: Context) -> LevelLightsView {
        let view = LevelLightsView()
        view.player = player
        return view
    }

    func updateNSView(_ view: LevelLightsView, context: Context) {}

    func sizeThatFits(_ proposal: ProposedViewSize, nsView: LevelLightsView, context: Context) -> CGSize? {
        LevelLightsView.size
    }
}
