import Foundation

/// A track as render.py describes it in tracks.json.
struct ManifestEntry: Decodable {
    let name: String
    let file: String
    let seconds: Double
    let title: String
    let titleKo: String?
    let style: String?
    let bpm: Double?
    let key: String?
}
