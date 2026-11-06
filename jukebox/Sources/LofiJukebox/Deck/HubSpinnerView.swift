import AppKit
import SwiftUI

/// The two cassette hubs, turned by Core Animation while the tape plays.
final class HubSpinnerView: NSView {
    private let root = CALayer()
    private let hubs = [CALayer(), CALayer()]
    private var isSpinning = false

    override init(frame: NSRect) {
        super.init(frame: frame)
        layer = root
        wantsLayer = true
        for hub in hubs {
            build(hub)
            root.addSublayer(hub)
            pause(hub)
        }
    }

    required init?(coder: NSCoder) {
        fatalError("HubSpinnerView is only made in code")
    }

    override func setFrameSize(_ newSize: NSSize) {
        super.setFrameSize(newSize)
        CATransaction.begin()
        CATransaction.setDisableActions(true)
        hubs[0].position = CGPoint(x: newSize.width * 0.25, y: newSize.height / 2)
        hubs[1].position = CGPoint(x: newSize.width * 0.75, y: newSize.height / 2)
        CATransaction.commit()
    }

    func setSpinning(_ spinning: Bool) {
        guard spinning != isSpinning else { return }
        isSpinning = spinning
        hubs.forEach(spinning ? resume : pause)
    }

    private func build(_ hub: CALayer) {
        hub.bounds = CGRect(x: 0, y: 0, width: 24, height: 24)
        let centre = CGPoint(x: 12, y: 12)

        let wheel = CAShapeLayer()
        wheel.path = CGPath(ellipseIn: CGRect(x: 1, y: 1, width: 22, height: 22), transform: nil)
        wheel.fillColor = NSColor(Palette.paperWhite).cgColor
        wheel.strokeColor = NSColor(Palette.ink).cgColor
        wheel.lineWidth = 2

        let teeth = CAShapeLayer()
        let path = CGMutablePath()
        for tooth in 0..<6 {
            let angle = Double(tooth) * .pi / 3
            path.move(to: CGPoint(x: centre.x + cos(angle) * 4, y: centre.y + sin(angle) * 4))
            path.addLine(to: CGPoint(x: centre.x + cos(angle) * 8.5, y: centre.y + sin(angle) * 8.5))
        }
        teeth.path = path
        teeth.strokeColor = NSColor(Palette.ink).cgColor
        teeth.lineWidth = 2.5
        teeth.lineCap = .round

        hub.addSublayer(wheel)
        hub.addSublayer(teeth)

        let spin = CABasicAnimation(keyPath: "transform.rotation.z")
        spin.fromValue = 0
        spin.toValue = -2 * Double.pi
        spin.duration = 1 / 0.7
        spin.repeatCount = .infinity
        hub.add(spin, forKey: "spin")
    }

    /// Freeze the hub where it is.
    private func pause(_ hub: CALayer) {
        let now = hub.convertTime(CACurrentMediaTime(), from: nil)
        hub.speed = 0
        hub.timeOffset = now
    }

    /// Carry on turning from where it stopped.
    private func resume(_ hub: CALayer) {
        let stoppedAt = hub.timeOffset
        hub.speed = 1
        hub.timeOffset = 0
        hub.beginTime = 0
        hub.beginTime = hub.convertTime(CACurrentMediaTime(), from: nil) - stoppedAt
    }
}
