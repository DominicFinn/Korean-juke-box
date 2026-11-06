import SwiftUI

/// Runs the app, or with `--render-icon <file.png>` draws the app icon and exits.
/// build.sh uses the second form so the icon matches the app's own artwork.
@main
enum Launch {
    @MainActor
    static func main() {
        let arguments = CommandLine.arguments
        if let flag = arguments.firstIndex(of: "--render-icon"), arguments.indices.contains(flag + 1) {
            IconRenderer.render(to: URL(filePath: arguments[flag + 1]))
        } else {
            LofiJukeboxApp.main()
        }
    }
}
