import SwiftUI

/// One tape on the shelf. The one that's playing slides out a little with a tag on it.
struct TapeSpine: View {
    let track: Track
    let number: Int
    let isCurrent: Bool
    let play: () -> Void

    var body: some View {
        Button(action: play) {
            HStack(spacing: 10) {
                Text(number, format: .number.precision(.integerLength(2)))
                    .font(.heavy(13, relativeTo: .body))
                    .frame(width: 30, height: 30)
                    .background(Palette.paperWhite, in: .circle)
                    .overlay { Circle().strokeBorder(Palette.ink, lineWidth: 2) }
                VStack(alignment: .leading, spacing: 1) {
                    Text(track.titleKo)
                        .font(.serif(14))
                    Text(track.title)
                        .font(.label(11, relativeTo: .caption))
                        .opacity(0.75)
                }
                .lineLimit(1)
                .minimumScaleFactor(0.7)
                Spacer(minLength: 4)
                VStack(alignment: .trailing, spacing: 0) {
                    Text(track.bpm > 0 ? String(Int(track.bpm.rounded())) : "")
                        .font(.heavy(13, relativeTo: .body))
                    Text(track.bpm > 0 ? "BPM" : "")
                        .font(.label(8, relativeTo: .caption2))
                }
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 8)
            .frame(maxWidth: .infinity, alignment: .leading)
            .contentShape(.rect)
        }
        .buttonStyle(StickerButtonStyle(fill: track.tapeColor, cornerRadius: 6))
        .overlay(alignment: .topTrailing) {
            Text("재생 중")
                .font(.heavy(9, relativeTo: .caption2))
                .foregroundStyle(Palette.paperWhite)
                .padding(.horizontal, 6)
                .padding(.vertical, 3)
                .background(Palette.sakuraDeep, in: .rect(cornerRadius: 3))
                .overlay { RoundedRectangle(cornerRadius: 3).strokeBorder(Palette.ink, lineWidth: 1.5) }
                .rotationEffect(.degrees(6))
                .offset(x: 4, y: -8)
                .opacity(isCurrent ? 1 : 0)
        }
        .offset(x: isCurrent ? -8 : 0)
        .animation(.snappy, value: isCurrent)
        .accessibilityLabel("\(track.title), \(track.details)")
        .accessibilityAddTraits(isCurrent ? .isSelected : [])
    }
}
