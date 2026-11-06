import Foundation

/// The tracks.json file render.py keeps next to the loops.
struct TrackManifest: Decodable {
    let tracks: [ManifestEntry]
}
