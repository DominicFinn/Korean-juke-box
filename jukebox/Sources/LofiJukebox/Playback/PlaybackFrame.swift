import Foundation

/// Where the current tape is, for the tape window and the readout.
struct PlaybackFrame: Sendable {
    /// Seconds the current tape has played, counting every time round the loop
    var elapsed: Double
    var loopSeconds: Double
    /// How many times each tape plays before the next one. 0 means it loops forever.
    var plays: Int

    var loopNumber: Int {
        loopSeconds > 0 ? Int(elapsed / loopSeconds) + 1 : 1
    }

    var positionInLoop: Double {
        loopSeconds > 0 ? elapsed.truncatingRemainder(dividingBy: loopSeconds) : 0
    }

    /// How far through its plays the tape is, which sets how much tape sits on each reel.
    var progress: Double {
        guard loopSeconds > 0 else { return 0 }
        if plays > 0 {
            return min(1, elapsed / (Double(plays) * loopSeconds))
        }
        return positionInLoop / loopSeconds
    }
}
