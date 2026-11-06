import SwiftUI

/// Which time round the loop it is, and the time.
struct DeckReadout: View {
    let frame: PlaybackFrame

    var body: some View {
        HStack(spacing: 12) {
            Text(loops)
                .font(.heavy(12, relativeTo: .caption))
            Text(time)
                .font(.system(size: 12, weight: .semibold, design: .rounded))
                .monospacedDigit()
        }
        .foregroundStyle(Palette.ink)
    }

    private var loops: String {
        frame.plays == 0 ? "반복 ∞" : "\(min(frame.loopNumber, frame.plays)) / \(frame.plays)"
    }

    private var time: String {
        let pattern = Duration.TimeFormatStyle(pattern: .minuteSecond)
        let position = Duration.seconds(frame.positionInLoop).formatted(pattern)
        let length = Duration.seconds(frame.loopSeconds).formatted(pattern)
        return "\(position) / \(length)"
    }
}
