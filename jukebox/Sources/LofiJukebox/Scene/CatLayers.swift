import QuartzCore

/// Oreo and Milo on the windowsill, animated by Core Animation. While music plays they sit
/// watching the city and bounce in time: Oreo on every beat, Milo lazily on every other
/// one. When it stops they curl up and doze.
@MainActor
final class CatLayers {
    let container = CALayer()
    private let oreo = CatRig()
    private let milo = CatRig()
    private let oreoAsleep = CatRig()
    private let miloAsleep = CatRig()

    init() {
        for cat in [oreoAsleep, miloAsleep, oreo, milo] {
            container.addSublayer(cat.rig)
        }
    }

    func build(layout: SceneLayout, bounds: CGRect, scale: Double, reduceMotion: Bool) {
        container.frame = bounds
        let feet = bounds.height - layout.catBase
        oreo.place(.oreoBack, height: 128, feet: CGPoint(x: layout.oreoX, y: feet), in: bounds, scale: scale)
        milo.place(.miloBack, height: 122, feet: CGPoint(x: layout.miloX, y: feet), in: bounds, scale: scale)
        oreoAsleep.place(.oreoLoaf, height: 92, feet: CGPoint(x: layout.oreoX - 8, y: feet), in: bounds, scale: scale)
        miloAsleep.place(.miloCurl, height: 104, feet: CGPoint(x: layout.miloX + 4, y: feet), in: bounds, scale: scale)

        for (cat, delay) in [(oreoAsleep, 0.0), (miloAsleep, 1.2)] {
            cat.sprite.removeAllAnimations()
            guard !reduceMotion else { continue }
            let breath = CABasicAnimation(keyPath: "transform.scale.y")
            breath.fromValue = 1.0
            breath.toValue = 1.0125
            breath.duration = 2.25
            breath.autoreverses = true
            breath.repeatCount = .infinity
            breath.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
            breath.timeOffset = delay
            cat.sprite.add(breath, forKey: "breath")
        }
    }

    /// Swap between awake and asleep, and line the bouncing up with the beat. `beats` is
    /// how far into the tape we are, counted in beats.
    func apply(isPlaying: Bool, bpm: Double, beats: Double, fade: Bool, reduceMotion: Bool) {
        CATransaction.begin()
        CATransaction.setAnimationDuration(fade && !reduceMotion ? 0.6 : 0)
        CATransaction.setDisableActions(!fade || reduceMotion)
        oreo.rig.opacity = isPlaying ? 1 : 0
        milo.rig.opacity = isPlaying ? 1 : 0
        oreoAsleep.rig.opacity = isPlaying ? 0 : 1
        miloAsleep.rig.opacity = isPlaying ? 0 : 1
        CATransaction.commit()

        oreo.sprite.removeAllAnimations()
        milo.sprite.removeAllAnimations()
        guard isPlaying, bpm > 0, !reduceMotion else { return }
        let beat = 60 / bpm

        // Oreo: squashes sharply on each beat and springs back, leaning one way then the other
        let squash = [0.0, 0.06, 0.15, 0.3, 0.5, 1.0].map { ($0, exp(-6 * $0)) }
        bounce(oreo.sprite, keyTimes: squash.map(\.0), amounts: squash.map(\.1), period: beat, beats: beats,
               beatsPerCycle: 1, linear: true)
        lean(oreo.sprite, degrees: 2, period: beat * 2, beats: beats, beatsPerCycle: 2)

        // Milo: a slow, heavy nod every other beat
        let nod = [0.0, 0.25, 0.5, 0.75, 1.0].map { ($0, 0.6 * (1 + cos(2 * .pi * $0)) / 2) }
        bounce(milo.sprite, keyTimes: nod.map(\.0), amounts: nod.map(\.1), period: beat * 2, beats: beats,
               beatsPerCycle: 2, linear: false)
        lean(milo.sprite, degrees: 1.2, period: beat * 4, beats: beats, beatsPerCycle: 4)
    }

    private func bounce(_ layer: CALayer, keyTimes: [Double], amounts: [Double], period: Double, beats: Double,
                        beatsPerCycle: Double, linear: Bool) {
        for (key, stretch) in [("transform.scale.y", -0.05), ("transform.scale.x", 0.025)] {
            let animation = CAKeyframeAnimation(keyPath: key)
            animation.values = amounts.map { 1 + stretch * $0 }
            animation.keyTimes = keyTimes.map { NSNumber(value: $0) }
            animation.calculationMode = linear ? .linear : .cubic
            loop(animation, on: layer, period: period, beats: beats, beatsPerCycle: beatsPerCycle, key: key)
        }
    }

    private func lean(_ layer: CALayer, degrees: Double, period: Double, beats: Double, beatsPerCycle: Double) {
        let animation = CAKeyframeAnimation(keyPath: "transform.rotation.z")
        animation.values = [0, 1, 0, -1, 0].map { $0 * degrees * .pi / 180 }
        animation.keyTimes = [0, 0.25, 0.5, 0.75, 1].map { NSNumber(value: $0) }
        animation.calculationMode = .cubic
        loop(animation, on: layer, period: period, beats: beats, beatsPerCycle: beatsPerCycle, key: "lean")
    }

    /// Repeat forever, started part-way through so the cycle lines up with the music.
    private func loop(_ animation: CAKeyframeAnimation, on layer: CALayer, period: Double, beats: Double,
                      beatsPerCycle: Double, key: String) {
        let into = beats.truncatingRemainder(dividingBy: beatsPerCycle) / beatsPerCycle
        animation.duration = period
        animation.repeatCount = .infinity
        animation.beginTime = layer.convertTime(CACurrentMediaTime(), from: nil) - into * period
        layer.add(animation, forKey: key)
    }
}
