import AVFoundation
import Observation

/// Keeps the list of tapes in step with the folder render.py writes to.
@MainActor
@Observable
final class TrackLibrary {
    private(set) var tracks: [Track] = []
    private(set) var folder: URL
    private(set) var problem: String?

    @ObservationIgnored private var fingerprint: [String: Date] = [:]
    private static let folderKey = "musicFolder"

    init() {
        if let saved = UserDefaults.standard.url(forKey: Self.folderKey) {
            folder = saved
        } else if let path = Bundle.main.object(forInfoDictionaryKey: "LofiMusicFolder") as? String {
            folder = URL(filePath: path, directoryHint: .isDirectory)
        } else {
            folder = URL.musicDirectory
        }
    }

    /// Checks the folder every couple of seconds, so a fresh render turns up on its own.
    func watch() async {
        while !Task.isCancelled {
            reloadIfChanged()
            try? await Task.sleep(for: .seconds(2))
        }
    }

    func use(folder: URL) {
        self.folder = folder
        UserDefaults.standard.set(folder, forKey: Self.folderKey)
        fingerprint = [:]
        reloadIfChanged()
    }

    private func reloadIfChanged() {
        let current = scan()
        guard current != fingerprint else { return }
        fingerprint = current
        tracks = load()
    }

    /// Where the loops actually are. Picking the music-electro project folder works too,
    /// because render.py writes into its out folder.
    private var tapes: URL {
        let manifest = "tracks.json"
        let rendered = folder.appending(path: "out")
        let fileManager = FileManager.default
        if !fileManager.fileExists(atPath: folder.appending(path: manifest).path(percentEncoded: false)),
           fileManager.fileExists(atPath: rendered.appending(path: manifest).path(percentEncoded: false)) {
            return rendered
        }
        return folder
    }

    /// File names and modification dates of the WAVs and the manifest.
    private func scan() -> [String: Date] {
        let files = (try? FileManager.default.contentsOfDirectory(
            at: tapes, includingPropertiesForKeys: [.contentModificationDateKey])) ?? []
        var result: [String: Date] = [:]
        for file in files where ["wav", "json"].contains(file.pathExtension) {
            let values = try? file.resourceValues(forKeys: [.contentModificationDateKey])
            result[file.lastPathComponent] = values?.contentModificationDate ?? .distantPast
        }
        return result
    }

    private func load() -> [Track] {
        let tapes = tapes
        var entries: [ManifestEntry] = []
        problem = nil
        if let data = try? Data(contentsOf: tapes.appending(path: "tracks.json")) {
            let decoder = JSONDecoder()
            decoder.keyDecodingStrategy = .convertFromSnakeCase
            do {
                entries = try decoder.decode(TrackManifest.self, from: data).tracks
            } catch {
                problem = "tracks.json을 읽을 수 없어요"
            }
        }

        var tracks = entries.compactMap { entry -> Track? in
            guard let modified = fingerprint[entry.file] else { return nil }
            return Track(
                id: entry.name,
                url: tapes.appending(path: entry.file),
                title: entry.title,
                titleKo: entry.titleKo ?? entry.title,
                style: entry.style ?? "",
                bpm: entry.bpm ?? 0,
                key: entry.key ?? "",
                seconds: entry.seconds,
                modified: modified
            )
        }

        // WAVs that aren't in the manifest still play, named after the file
        let listed = Set(entries.map(\.file))
        for file in fingerprint.keys.sorted() where file.hasSuffix(".wav") && !listed.contains(file) {
            let url = tapes.appending(path: file)
            guard let audio = try? AVAudioFile(forReading: url) else { continue }
            let name = url.deletingPathExtension().lastPathComponent
            let title = name.replacing("_", with: " ").capitalized
            tracks.append(Track(
                id: name, url: url, title: title, titleKo: title, style: "", bpm: 0, key: "",
                seconds: Double(audio.length) / audio.fileFormat.sampleRate,
                modified: fingerprint[file] ?? .distantPast
            ))
        }
        return tracks
    }
}
