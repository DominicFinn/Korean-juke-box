import AppKit

/// `--snapshot <file.png>` saves a picture of the window after a few seconds and quits.
enum DebugSnapshot {
    @MainActor
    static func scheduleIfRequested() {
        let arguments = CommandLine.arguments
        guard let flag = arguments.firstIndex(of: "--snapshot"), arguments.indices.contains(flag + 1) else { return }
        let url = URL(filePath: arguments[flag + 1])
        let delay = arguments.firstIndex(of: "--delay").flatMap { Double(arguments[$0 + 1]) } ?? 3
        Task { @MainActor in
            try? await Task.sleep(for: .seconds(delay))
            guard let view = NSApp.windows.first(where: \.isVisible)?.contentView,
                  let rep = view.bitmapImageRepForCachingDisplay(in: view.bounds) else { return }
            view.cacheDisplay(in: view.bounds, to: rep)
            try? rep.representation(using: .png, properties: [:])?.write(to: url)
            NSApp.terminate(nil)
        }
    }
}
