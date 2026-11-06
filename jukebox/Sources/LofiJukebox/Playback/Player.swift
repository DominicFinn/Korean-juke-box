import AVFoundation
import Observation

/// Plays loops gaplessly and works through the playlist like a jukebox: each tape plays
/// `playsPerTrack` times, then crossfades into the next.
@MainActor
@Observable
final class Player {
    static let playRange = 1...8

    private(set) var current: Track?
    private(set) var isPlaying = false
    private(set) var playlist: [Track] = []
    private(set) var problem: String?

    var playsPerTrack = UserDefaults.standard.object(forKey: "playsPerTrack") as? Int ?? 2 {
        didSet { UserDefaults.standard.set(playsPerTrack, forKey: "playsPerTrack") }
    }

    var shuffle = UserDefaults.standard.bool(forKey: "shuffle") {
        didSet { UserDefaults.standard.set(shuffle, forKey: "shuffle") }
    }

    /// Keep looping the current tape instead of moving on. Handy for checking a loop's seam.
    var repeatOne = UserDefaults.standard.bool(forKey: "repeatOne") {
        didSet { UserDefaults.standard.set(repeatOne, forKey: "repeatOne") }
    }

    var volume = UserDefaults.standard.object(forKey: "volume") as? Double ?? 0.8 {
        didSet {
            engine.mainMixerNode.outputVolume = Float(volume)
            UserDefaults.standard.set(volume, forKey: "volume")
        }
    }

    /// Output loudness from 0 to 1, for the neon and the level lights.
    var level: Double {
        isPlaying ? meter.level : 0
    }

    /// The current tape's position in the playlist, counting from 1.
    var currentNumber: Int? {
        playlist.firstIndex { $0.id == current?.id }.map { $0 + 1 }
    }

    @ObservationIgnored private let engine = AVAudioEngine()
    /// Two decks, so one tape can fade out while the next fades in
    @ObservationIgnored private let decks = [AVAudioPlayerNode(), AVAudioPlayerNode()]
    @ObservationIgnored private var active = 0
    @ObservationIgnored private var cache: [URL: (modified: Date, buffer: AVAudioPCMBuffer)] = [:]
    @ObservationIgnored private let meter = LevelMeter()
    @ObservationIgnored private let nowPlaying = NowPlayingBridge()
    @ObservationIgnored private var fade: Task<Void, Never>?
    @ObservationIgnored private var autoAdvance: Task<Void, Never>?
    @ObservationIgnored private var outputWatch: Task<Void, Never>?
    @ObservationIgnored private var lastElapsed = 0.0
    @ObservationIgnored private var hasStarted = false

    private static let autoFadeSeconds = 4.0

    init() {
        for deck in decks {
            engine.attach(deck)
            engine.connect(deck, to: engine.mainMixerNode, format: nil)
        }
        engine.mainMixerNode.outputVolume = Float(volume)
        meter.attach(to: engine.mainMixerNode)
        nowPlaying.connect(to: self)

        autoAdvance = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(for: .milliseconds(250))
                self?.advanceIfDue()
            }
        }

        // Plugging in headphones or switching speakers stops the engine. Pick up where
        // we were on the new output.
        outputWatch = Task { [weak self] in
            for await _ in NotificationCenter.default.notifications(named: .AVAudioEngineConfigurationChange) {
                self?.restartAfterOutputChange()
            }
        }
    }

    // MARK: Controls

    func play(_ track: Track, fade duration: Duration = .seconds(0.8)) {
        let buffer: AVAudioPCMBuffer
        do {
            buffer = try loadBuffer(for: track)
        } catch {
            problem = "\(track.url.lastPathComponent) 파일을 열 수 없어요"
            return
        }

        let outgoing = decks[active]
        active = 1 - active
        let incoming = decks[active]
        incoming.stop()
        if incoming.outputFormat(forBus: 0) != buffer.format {
            engine.disconnectNodeOutput(incoming)
            engine.connect(incoming, to: engine.mainMixerNode, format: buffer.format)
        }
        // .loops repeats the buffer sample-accurately, so the seam stays seamless
        incoming.scheduleBuffer(buffer, at: nil, options: .loops, completionHandler: nil)
        incoming.volume = 0
        guard startEngine() else { return }
        incoming.play()

        problem = nil
        current = track
        isPlaying = true
        hasStarted = true
        lastElapsed = 0
        crossfade(from: outgoing, to: incoming, over: duration)
        updateNowPlaying()
    }

    func togglePlay() {
        if isPlaying {
            pause()
        } else if current != nil {
            resume()
        } else if let first = playlist.first {
            play(first)
        }
    }

    func pause() {
        guard isPlaying else { return }
        engine.pause()
        isPlaying = false
        meter.reset()
        updateNowPlaying()
    }

    func resume() {
        guard !isPlaying, current != nil, startEngine() else { return }
        isPlaying = true
        updateNowPlaying()
    }

    func skipForward() {
        if let track = neighbour(offset: 1) {
            play(track)
        }
    }

    func skipBack() {
        if let track = neighbour(offset: -1) {
            play(track)
        }
    }

    /// Called whenever the library changes. Starts the first tape on launch, and swaps in
    /// a new version of the playing tape if it was re-rendered.
    func setPlaylist(_ tracks: [Track]) {
        playlist = tracks
        if !hasStarted, let first = tracks.first {
            play(first, fade: .seconds(1.5))
        } else if let current, let updated = tracks.first(where: { $0.id == current.id }),
                  updated.modified != current.modified {
            if isPlaying {
                play(updated, fade: .seconds(0.5))
            } else {
                self.current = updated
            }
        }
    }

    // MARK: Position

    /// Seconds the current tape has been playing, counting every time round the loop.
    func elapsed() -> Double {
        let deck = decks[active]
        if let renderTime = deck.lastRenderTime, let time = deck.playerTime(forNodeTime: renderTime) {
            lastElapsed = max(0, Double(time.sampleTime) / time.sampleRate)
        }
        return lastElapsed
    }

    func frame() -> PlaybackFrame {
        PlaybackFrame(
            elapsed: elapsed(),
            loopSeconds: current?.seconds ?? 0,
            plays: repeatOne || playlist.count < 2 ? 0 : playsPerTrack
        )
    }

    // MARK: Internals

    private func advanceIfDue() {
        guard isPlaying, !repeatOne, playlist.count > 1, let current else { return }
        let planned = Double(playsPerTrack) * current.seconds
        if elapsed() >= planned - Self.autoFadeSeconds, let track = neighbour(offset: 1) {
            play(track, fade: .seconds(Self.autoFadeSeconds))
        }
    }

    private func restartAfterOutputChange() {
        guard isPlaying, let current else { return }
        isPlaying = false
        play(current, fade: .seconds(0.3))
    }

    private func neighbour(offset: Int) -> Track? {
        guard !playlist.isEmpty else { return nil }
        if shuffle, playlist.count > 1 {
            return playlist.filter { $0.id != current?.id }.randomElement()
        }
        let index = playlist.firstIndex { $0.id == current?.id } ?? -offset
        return playlist[(index + offset + playlist.count) % playlist.count]
    }

    private func crossfade(from outgoing: AVAudioPlayerNode, to incoming: AVAudioPlayerNode, over duration: Duration) {
        fade?.cancel()
        let startVolume = outgoing.volume
        let steps = max(1, Int((duration / .milliseconds(20)).rounded()))
        fade = Task {
            for step in 1...steps {
                try? await Task.sleep(for: .milliseconds(20))
                guard !Task.isCancelled else { return }
                // Equal-power curves, so the middle of the fade doesn't dip in volume
                let x = Float(step) / Float(steps)
                incoming.volume = sin(x * .pi / 2)
                outgoing.volume = startVolume * cos(x * .pi / 2)
            }
            outgoing.stop()
        }
    }

    private func startEngine() -> Bool {
        guard !engine.isRunning else { return true }
        do {
            try engine.start()
            return true
        } catch {
            problem = "오디오 출력을 시작할 수 없어요"
            return false
        }
    }

    private func loadBuffer(for track: Track) throws -> AVAudioPCMBuffer {
        if let cached = cache[track.url], cached.modified == track.modified {
            return cached.buffer
        }
        let file = try AVAudioFile(forReading: track.url)
        guard let buffer = AVAudioPCMBuffer(pcmFormat: file.processingFormat,
                                            frameCapacity: AVAudioFrameCount(file.length)) else {
            throw CocoaError(.fileReadCorruptFile)
        }
        try file.read(into: buffer)
        cache[track.url] = (track.modified, buffer)
        return buffer
    }

    private func updateNowPlaying() {
        nowPlaying.update(track: current, isPlaying: isPlaying, elapsed: lastElapsed)
    }
}
