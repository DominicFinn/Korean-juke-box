import AppKit
import SwiftUI

/// A row of little lights showing how loud it is. Updated ten times a second straight
/// onto the layers, without going through SwiftUI.
final class LevelLightsView: NSView {
    static let count = 10
    static let size = CGSize(width: Double(count) * 7 + Double(count - 1) * 3, height: 14)

    weak var player: Player?

    private let root = CALayer()
    private var lights: [CALayer] = []
    private var shown = -1
    private var meter: Task<Void, Never>?

    override init(frame: NSRect) {
        super.init(frame: frame)
        layer = root
        wantsLayer = true
        for index in 0..<Self.count {
            let light = CALayer()
            light.frame = CGRect(x: Double(index) * 10, y: 0, width: 7, height: 14)
            light.cornerRadius = 3.5
            light.borderWidth = 1
            light.borderColor = NSColor(Palette.ink).cgColor
            root.addSublayer(light)
            lights.append(light)
        }
        show(0)
    }

    required init?(coder: NSCoder) {
        fatalError("LevelLightsView is only made in code")
    }

    override func viewDidMoveToWindow() {
        super.viewDidMoveToWindow()
        meter?.cancel()
        guard window != nil else { return }
        meter = Task { [weak self] in
            while !Task.isCancelled {
                if let self {
                    show(Int((player?.level ?? 0) * Double(Self.count)))
                }
                try? await Task.sleep(for: .milliseconds(100))
            }
        }
    }

    private func show(_ lit: Int) {
        guard lit != shown else { return }
        shown = lit
        CATransaction.begin()
        CATransaction.setAnimationDuration(0.08)
        for (index, light) in lights.enumerated() {
            light.backgroundColor = NSColor(color(for: index)).withAlphaComponent(index < lit ? 1 : 0.18).cgColor
        }
        CATransaction.commit()
    }

    private func color(for index: Int) -> Color {
        switch index {
        case 0..<6: Palette.matcha
        case 6..<9: Palette.yuzu
        default: Palette.sakuraDeep
        }
    }
}
