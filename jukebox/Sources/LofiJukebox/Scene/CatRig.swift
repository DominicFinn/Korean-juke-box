import QuartzCore

/// One cat sprite with its shadow. The rig fades in and out; the sprite bounces.
@MainActor
final class CatRig {
    let rig = CALayer()
    let sprite = CALayer()
    private let shadow = CAShapeLayer()

    init() {
        rig.addSublayer(shadow)
        rig.addSublayer(sprite)
        // Feet stay put while the cat squashes and leans
        sprite.anchorPoint = CGPoint(x: 0.5, y: 0)
        sprite.contentsGravity = .resizeAspect
    }

    /// `feet` is in the layer's own coordinates, where y counts up from the bottom.
    func place(_ pose: CatPose, height: Double, feet: CGPoint, in bounds: CGRect, scale: Double) {
        rig.frame = bounds
        guard let image = pose.cgImage else { return }
        let width = height * Double(image.width) / Double(image.height)
        sprite.contents = image
        sprite.contentsScale = scale
        sprite.bounds = CGRect(x: 0, y: 0, width: width, height: height)
        sprite.position = feet
        shadow.path = CGPath(ellipseIn: CGRect(x: feet.x - width / 2 + 6, y: feet.y - 5, width: width - 12, height: 10),
                             transform: nil)
        shadow.fillColor = CGColor(red: 0.12, green: 0.10, blue: 0.09, alpha: 0.3)
    }
}
