import AppKit
import SwiftUI

/// The window scene, animated by Core Animation. SwiftUI paints the still parts once, as
/// images. The rain, the bouncing cats, the twinkling and the flickering all run in the
/// system's render server, so the app itself sits idle while it plays. Layers use AppKit's
/// usual coordinates, with y counting up from the bottom.
final class NightSceneView: NSView {
    struct State: Equatable {
        /// Changes when a different tape starts, or the same one is re-rendered
        var tape: String?
        var isPlaying = false
        var bpm = 0.0
        var reduceMotion = false
    }

    weak var player: Player?

    private var state = State()
    private var builtSize = CGSize.zero
    private let root = CALayer()
    private let backdrop = CALayer()
    private let twinkles = CALayer()
    private let lights = CALayer()
    private let rain = CAEmitterLayer()
    private let foreground = CALayer()
    private let steam = CALayer()
    private let cats = CatLayers()
    private let notes = CAEmitterLayer()
    private let dozing = CAEmitterLayer()
    private var halos: [(layer: CALayer, floor: Double)] = []
    private var glow: Task<Void, Never>?

    override init(frame: NSRect) {
        super.init(frame: frame)
        layer = root
        wantsLayer = true
        root.masksToBounds = true
        for sublayer in [backdrop, twinkles, lights, rain, foreground, steam, cats.container, notes, dozing] {
            root.addSublayer(sublayer)
        }
    }

    required init?(coder: NSCoder) {
        fatalError("NightSceneView is only made in code")
    }

    func update(_ newState: State) {
        let previous = state
        state = newState
        if newState.reduceMotion != previous.reduceMotion {
            builtSize = .zero
        }
        if builtSize != bounds.size {
            rebuild()
        } else if newState != previous {
            apply(fade: newState.isPlaying != previous.isPlaying)
        }
    }

    // MARK: Lifecycle

    override func viewDidMoveToWindow() {
        super.viewDidMoveToWindow()
        glow?.cancel()
        guard window != nil else { return }
        rebuild()
        glow = Task { [weak self] in
            while !Task.isCancelled {
                self?.updateGlow()
                try? await Task.sleep(for: .milliseconds(100))
            }
        }
    }

    override func setFrameSize(_ newSize: NSSize) {
        super.setFrameSize(newSize)
        // Repainting the backdrop on every step of a live resize would stutter, so the
        // images stretch until the drag ends
        if !inLiveResize {
            rebuild()
        }
    }

    override func viewDidEndLiveResize() {
        super.viewDidEndLiveResize()
        rebuild()
    }

    // MARK: Building

    private func rebuild() {
        let size = bounds.size
        guard window != nil, size.width > 0, size.height > 0, size != builtSize else { return }
        builtSize = size
        let layout = SceneLayout(size: size)
        let scale = window?.backingScaleFactor ?? 2

        CATransaction.begin()
        CATransaction.setDisableActions(true)
        for sublayer in [backdrop, twinkles, lights, rain, foreground, steam, notes, dozing] {
            sublayer.frame = bounds
        }
        backdrop.contents = SceneArt.image(SceneBackdrop(layout: layout), scale: scale)
        foreground.contents = SceneArt.image(SceneForeground(layout: layout), scale: scale)
        buildTwinkles(layout)
        buildLights(layout, scale: scale)
        buildRain(scale: scale)
        buildSteam(layout)
        cats.build(layout: layout, bounds: bounds, scale: scale, reduceMotion: state.reduceMotion)
        buildDozing(layout, scale: scale)
        CATransaction.commit()

        apply(fade: false)
    }

    /// Top-left coordinates, as SceneLayout uses, to the layers' bottom-left ones.
    private func flip(_ point: CGPoint) -> CGPoint {
        CGPoint(x: point.x, y: bounds.height - point.y)
    }

    private func flip(_ rect: CGRect) -> CGRect {
        CGRect(x: rect.minX, y: bounds.height - rect.maxY, width: rect.width, height: rect.height)
    }

    private func buildTwinkles(_ layout: SceneLayout) {
        twinkles.sublayers = nil
        for star in StarField.stars(in: layout) {
            let sparkle = CAShapeLayer()
            sparkle.path = StarField.sparkle(at: .zero, radius: star.radius).cgPath
            sparkle.fillColor = NSColor(Palette.moon).cgColor
            sparkle.position = flip(star.point)
            sparkle.opacity = 0.7
            if !state.reduceMotion {
                let twinkle = CABasicAnimation(keyPath: "opacity")
                twinkle.fromValue = 0.35
                twinkle.toValue = 1.0
                twinkle.duration = .pi / star.speed
                twinkle.autoreverses = true
                twinkle.repeatCount = .infinity
                twinkle.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
                twinkle.timeOffset = star.phase / star.speed
                sparkle.add(twinkle, forKey: "twinkle")
            }
            twinkles.addSublayer(sparkle)
        }
    }

    private func buildLights(_ layout: SceneLayout, scale: Double) {
        lights.sublayers = nil
        halos = []

        // Windows that switch on and off, each on its own slow pattern
        for window in Skyline.flickeringWindows(in: layout) {
            let pane = CALayer()
            pane.frame = flip(window.rect)
            pane.backgroundColor = NSColor(window.color).cgColor
            let slots = 12
            let pattern = (0..<slots).map { SeededRandom.noise(window.seed, UInt64($0)) < 0.5 ? 1.0 : 0.0 }
            pane.opacity = Float(pattern[0])
            if !state.reduceMotion {
                let flicker = CAKeyframeAnimation(keyPath: "opacity")
                flicker.values = pattern + [pattern[0]]
                flicker.keyTimes = (0...slots).map { NSNumber(value: Double($0) / Double(slots)) }
                flicker.calculationMode = .discrete
                flicker.duration = Double(slots) * 6
                flicker.repeatCount = .infinity
                flicker.timeOffset = SeededRandom.noise(window.seed, 99) * flicker.duration
                pane.add(flicker, forKey: "flicker")
            }
            lights.addSublayer(pane)
        }

        // Red aircraft lights on the masts, blinking slowly
        for (index, top) in Skyline.warningLights(in: layout).enumerated() {
            let light = CALayer()
            light.bounds = CGRect(x: 0, y: 0, width: 5, height: 5)
            light.cornerRadius = 2.5
            light.position = flip(top)
            light.backgroundColor = CGColor(red: 1, green: 0.1, blue: 0.1, alpha: 0.9)
            if !state.reduceMotion {
                let blink = CAKeyframeAnimation(keyPath: "opacity")
                blink.values = [1, 0, 1]
                blink.keyTimes = [0, 0.4, 1]
                blink.calculationMode = .discrete
                blink.duration = 2.85
                blink.repeatCount = .infinity
                blink.timeOffset = Double(index) * 1.1
                light.add(blink, forKey: "blink")
            }
            lights.addSublayer(light)
        }

        // Neon signs, whose halos follow the music (see updateGlow)
        for sign in Skyline.signs(in: layout) {
            let frame = flip(CGRect(origin: sign.origin, size: sign.size))
            let halo = CALayer()
            halo.frame = frame.insetBy(dx: -NeonHaloArt.spread, dy: -NeonHaloArt.spread)
            halo.contents = SceneArt.image(NeonHaloArt(placement: sign), scale: scale)
            halo.opacity = 0.55
            lights.addSublayer(halo)
            halos.append((halo, sign.floor))

            let board = CALayer()
            board.frame = frame
            board.contents = SceneArt.image(NeonSignArt(placement: sign), scale: scale)
            lights.addSublayer(board)
        }
    }

    private func buildRain(scale: Double) {
        let size = bounds.size
        rain.emitterShape = .line
        rain.emitterPosition = CGPoint(x: size.width * 0.6, y: size.height + 24)
        rain.emitterSize = CGSize(width: size.width * 1.4, height: 1)
        let streak = SceneArt.rainStreak(scale: scale)

        func drops(alpha: Double, speed: Double, spread: Double, perSecond: Float, size: Double) -> CAEmitterCell {
            let cell = CAEmitterCell()
            cell.contents = streak
            cell.contentsScale = scale
            cell.color = NSColor(Palette.rain).withAlphaComponent(alpha).cgColor
            cell.velocity = speed
            cell.velocityRange = spread
            // Straight down, leaning a little to the left
            cell.emissionLongitude = -.pi / 2 - 0.16
            cell.lifetime = Float((bounds.height + 60) / (speed - spread))
            cell.birthRate = perSecond
            cell.scale = size
            return cell
        }

        rain.emitterCells = [
            drops(alpha: 0.25, speed: 360, spread: 60, perSecond: 80, size: 0.45),
            drops(alpha: 0.42, speed: 610, spread: 90, perSecond: 45, size: 0.75),
        ]
        rain.birthRate = state.reduceMotion ? 0 : 1
        // Start as if it's already been raining for a while
        rain.beginTime = CACurrentMediaTime() - 3
    }

    private func buildSteam(_ layout: SceneLayout) {
        steam.sublayers = nil
        guard !state.reduceMotion else { return }
        for wisp in 0..<3 {
            var path = Path()
            for step in 0...14 {
                let rise = Double(step) * 3
                let x = sin(rise * 0.12 + Double(wisp) * 2) * (2 + rise * 0.08)
                if step == 0 { path.move(to: CGPoint(x: x, y: rise)) } else { path.addLine(to: CGPoint(x: x, y: rise)) }
            }
            let line = CAShapeLayer()
            line.path = path.cgPath
            line.strokeColor = NSColor(Palette.moon).cgColor
            line.fillColor = nil
            line.lineWidth = 2
            line.lineCap = .round
            line.position = flip(CGPoint(x: layout.mugX - 7 + Double(wisp) * 7, y: layout.sillTop - 32))
            line.opacity = 0

            let rise = CABasicAnimation(keyPath: "position.y")
            rise.byValue = 12
            let fade = CAKeyframeAnimation(keyPath: "opacity")
            fade.values = [0, 0.6, 0]
            fade.keyTimes = [0, 0.35, 1]
            let puff = CAAnimationGroup()
            puff.animations = [rise, fade]
            puff.duration = 2.6
            puff.repeatCount = .infinity
            puff.timeOffset = Double(wisp) * 0.87
            line.add(puff, forKey: "steam")
            steam.addSublayer(line)
        }
    }

    private func buildDozing(_ layout: SceneLayout, scale: Double) {
        let z = CAEmitterCell()
        z.contents = SceneArt.glyph("z", font: .custom("AppleSDGothicNeo-Medium", size: 15), color: Palette.moon, scale: scale)
        z.contentsScale = scale
        z.birthRate = 0.8
        z.lifetime = 3
        z.velocity = 14
        z.emissionLongitude = .pi / 2 + 0.5
        z.scale = 0.7
        z.scaleSpeed = 0.2
        z.alphaSpeed = -0.33
        dozing.emitterShape = .point
        dozing.emitterPosition = flip(CGPoint(x: layout.catHead.x - 30, y: layout.catHead.y + 40))
        dozing.emitterCells = [z]
    }

    /// Notes float up from Milo about every other beat, so they come faster for faster tapes.
    private func notesCells(bpm: Double, scale: Double) -> [CAEmitterCell] {
        let beat = 60 / max(bpm, 40)
        return ["♪", "♫"].map { glyph in
            let note = CAEmitterCell()
            note.contents = SceneArt.glyph(glyph, font: .system(size: 17, weight: .bold), color: Palette.moon, scale: scale)
            note.contentsScale = scale
            note.birthRate = Float(1 / (beat * 4))
            note.lifetime = Float(beat * 8)
            note.velocity = 20
            note.velocityRange = 4
            note.emissionLongitude = .pi / 2 - 0.5
            note.emissionRange = 0.25
            note.alphaSpeed = -1 / note.lifetime
            return note
        }
    }

    // MARK: State

    private func apply(fade: Bool) {
        guard builtSize != .zero else { return }
        let layout = SceneLayout(size: bounds.size)
        let scale = window?.backingScaleFactor ?? 2
        let beats = (player?.elapsed() ?? 0) * state.bpm / 60
        cats.apply(isPlaying: state.isPlaying, bpm: state.bpm, beats: beats, fade: fade, reduceMotion: state.reduceMotion)

        CATransaction.begin()
        CATransaction.setDisableActions(true)
        notes.emitterShape = .point
        notes.emitterPosition = flip(CGPoint(x: layout.catHead.x + 30, y: layout.catHead.y - 10))
        notes.emitterCells = notesCells(bpm: state.bpm, scale: scale)
        notes.birthRate = state.isPlaying && !state.reduceMotion ? 1 : 0
        dozing.birthRate = !state.isPlaying && !state.reduceMotion ? 1 : 0
        CATransaction.commit()
    }

    /// Ten times a second, set how brightly the neon glows from how loud the music is,
    /// with the odd flicker. This is the only regular work the app does for the scene.
    private func updateGlow() {
        let level = player?.level ?? 0
        let flicker = state.reduceMotion || Double.random(in: 0...1) > 0.04 ? 1.0 : 0.35
        CATransaction.begin()
        CATransaction.setAnimationDuration(0.12)
        for halo in halos {
            halo.layer.opacity = Float(max(halo.floor, 0.55 + 0.45 * level) * flicker)
        }
        CATransaction.commit()
    }
}
