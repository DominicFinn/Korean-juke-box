import AVFoundation
import os

/// Measures how loud the output is. The tap runs on the audio thread, so the reading
/// lives behind a lock rather than on the main actor.
final class LevelMeter: Sendable {
    private let reading = OSAllocatedUnfairLock(initialState: Float.zero)

    var level: Double {
        Double(reading.withLock { $0 })
    }

    func reset() {
        reading.withLock { $0 = 0 }
    }

    func attach(to node: AVAudioNode) {
        node.installTap(onBus: 0, bufferSize: 2048, format: nil) { @Sendable [reading] buffer, _ in
            guard let channels = buffer.floatChannelData else { return }
            let frames = Int(buffer.frameLength)
            let count = Int(buffer.format.channelCount)
            guard frames > 0, count > 0 else { return }

            var sum: Float = 0
            for channel in 0..<count {
                let samples = channels[channel]
                for i in 0..<frames {
                    sum += samples[i] * samples[i]
                }
            }
            let rms = (sum / Float(frames * count)).squareRoot()

            // -42 to -6 dBFS maps onto 0 to 1. Rise fast, fall slowly, like a VU needle.
            let target = min(1, max(0, (20 * log10(max(rms, 1e-6)) + 42) / 36))
            reading.withLock { $0 = target > $0 ? target : $0 * 0.8 + target * 0.2 }
        }
    }
}
