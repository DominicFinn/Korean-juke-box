import SwiftUI

/// The paper label on the cassette, with the title written on it.
struct CassetteLabel: View {
    let track: Track?

    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            HStack(spacing: 6) {
                Text("A")
                    .font(.heavy(11))
                    .foregroundStyle(Palette.paperWhite)
                    .frame(width: 19, height: 19)
                    .background(Palette.sakuraDeep, in: .circle)
                Text(track?.titleKo ?? "테이프 없음")
                    .font(.serif(16, relativeTo: .headline))
                    .lineLimit(1)
                    .minimumScaleFactor(0.7)
                Spacer(minLength: 4)
                Text(track?.details ?? "")
                    .font(.label(9, relativeTo: .caption2))
                    .lineLimit(1)
                    .opacity(0.7)
            }
            Text(track?.title ?? "")
                .font(.label(12, relativeTo: .caption))
                .lineLimit(1)
                .opacity(0.7)
                .padding(.leading, 25)
            Spacer(minLength: 0)
        }
        .foregroundStyle(Palette.ink)
        .padding(8)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background {
            RoundedRectangle(cornerRadius: 6)
                .fill(Palette.paperWhite)
                .overlay(alignment: .top) {
                    VStack(spacing: 9) {
                        ForEach(0..<3, id: \.self) { _ in
                            Rectangle().fill(Palette.sakura.opacity(0.6)).frame(height: 1)
                        }
                    }
                    .padding(.horizontal, 8)
                    .padding(.top, 50)
                }
        }
        .overlay {
            RoundedRectangle(cornerRadius: 6).strokeBorder(Palette.ink, lineWidth: 2)
        }
    }
}
