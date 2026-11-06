import SwiftUI

struct SpinningHubs: NSViewRepresentable {
    let isSpinning: Bool

    func makeNSView(context: Context) -> HubSpinnerView {
        HubSpinnerView()
    }

    func updateNSView(_ view: HubSpinnerView, context: Context) {
        view.setSpinning(isSpinning)
    }
}
