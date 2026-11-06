import SwiftUI

struct ShelfHeader: View {
    let count: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline, spacing: 8) {
                Text("테이프 선반")
                    .font(.heavy(24))
                Spacer()
                Text("\(count)개")
                    .font(.label(12, relativeTo: .caption))
                    .accessibilityLabel("\(count) tapes")
            }
            Rectangle()
                .fill(Palette.ink)
                .frame(height: 3)
        }
        .foregroundStyle(Palette.ink)
    }
}
