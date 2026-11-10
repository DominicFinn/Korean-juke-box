import AppKit

/// `--snapshot <file.png>` saves a picture of the window after a few seconds and quits.
/// `--delay <seconds>` changes the wait, and `--paused` pauses first so the cats are
/// asleep. The window is set to a standard size so pictures match from run to run.
enum DebugSnapshot {
    static let windowSize = NSSize(width: 980, height: 700)

    @MainActor
    static func scheduleIfRequested(player: Player) {
        let arguments = CommandLine.arguments
        guard let flag = arguments.firstIndex(of: "--snapshot"), arguments.indices.contains(flag + 1) else { return }
        let url = URL(filePath: arguments[flag + 1])
        let delay = arguments.firstIndex(of: "--delay").flatMap { Double(arguments[$0 + 1]) } ?? 3
        let paused = arguments.contains("--paused")
        Task { @MainActor in
            try? await Task.sleep(for: .seconds(delay))
            guard let window = NSApp.windows.first(where: \.isVisible), let view = window.contentView else { return }
            window.setContentSize(windowSize)
            if paused {
                player.pause()
            }
            // Time for the scene to repaint at the new size and the cats to change pose
            try? await Task.sleep(for: .seconds(1.2))
            scene(in: view)?.showStillParticles()
            try? await Task.sleep(for: .milliseconds(200))
            guard let rep = view.bitmapImageRepForCachingDisplay(in: view.bounds) else { return }
            view.cacheDisplay(in: view.bounds, to: rep)
            try? rep.representation(using: .png, properties: [:])?.write(to: url)
            NSApp.terminate(nil)
        }
    }

    @MainActor
    private static func scene(in view: NSView) -> NightSceneView? {
        if let scene = view as? NightSceneView {
            return scene
        }
        for subview in view.subviews {
            if let scene = scene(in: subview) {
                return scene
            }
        }
        return nil
    }
}
