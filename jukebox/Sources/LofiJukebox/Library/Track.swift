import Foundation

/// One rendered loop: the WAV plus what render.py wrote about it in tracks.json.
struct Track: Identifiable, Hashable, Sendable {
    let id: String
    let url: URL
    let title: String
    let titleKo: String
    let style: String
    let bpm: Double
    let key: String
    let seconds: Double
    /// When the WAV last changed, so a re-render can be swapped in while playing
    let modified: Date
}
