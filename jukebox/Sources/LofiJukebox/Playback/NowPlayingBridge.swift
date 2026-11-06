import MediaPlayer

/// Connects the player to the keyboard's media keys and the Now Playing menu.
@MainActor
final class NowPlayingBridge {
    func connect(to player: Player) {
        let center = MPRemoteCommandCenter.shared()
        center.togglePlayPauseCommand.addTarget { @Sendable [weak player] _ in
            guard let player else { return .noActionableNowPlayingItem }
            Task { @MainActor in player.togglePlay() }
            return .success
        }
        center.playCommand.addTarget { @Sendable [weak player] _ in
            guard let player else { return .noActionableNowPlayingItem }
            Task { @MainActor in player.resume() }
            return .success
        }
        center.pauseCommand.addTarget { @Sendable [weak player] _ in
            guard let player else { return .noActionableNowPlayingItem }
            Task { @MainActor in player.pause() }
            return .success
        }
        center.nextTrackCommand.addTarget { @Sendable [weak player] _ in
            guard let player else { return .noActionableNowPlayingItem }
            Task { @MainActor in player.skipForward() }
            return .success
        }
        center.previousTrackCommand.addTarget { @Sendable [weak player] _ in
            guard let player else { return .noActionableNowPlayingItem }
            Task { @MainActor in player.skipBack() }
            return .success
        }
    }

    func update(track: Track?, isPlaying: Bool, elapsed: Double) {
        let center = MPNowPlayingInfoCenter.default()
        guard let track else {
            center.nowPlayingInfo = nil
            center.playbackState = .stopped
            return
        }
        center.nowPlayingInfo = [
            MPMediaItemPropertyTitle: track.title,
            MPMediaItemPropertyArtist: track.titleKo,
            MPMediaItemPropertyAlbumTitle: "아빠의 멋진 로파이 앱",
            MPMediaItemPropertyPlaybackDuration: track.seconds,
            MPNowPlayingInfoPropertyElapsedPlaybackTime: elapsed.truncatingRemainder(dividingBy: max(track.seconds, 1)),
            MPNowPlayingInfoPropertyPlaybackRate: isPlaying ? 1.0 : 0.0,
        ]
        center.playbackState = isPlaying ? .playing : .paused
    }
}
