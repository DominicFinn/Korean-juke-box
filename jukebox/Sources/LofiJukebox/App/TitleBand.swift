import SwiftUI

/// The strip across the top of the page, like a comic magazine's running head:
/// "Dad's Cool Lofi App".
struct TitleBand: View {
    var body: some View {
        HStack(spacing: 10) {
            Text("♪")
            Text("아빠의 멋진 로파이 앱")
                .font(.heavy(15, relativeTo: .headline))
            Text("♪")
        }
        .foregroundStyle(Palette.ink)
        .frame(maxWidth: .infinity)
        .frame(height: 26)
        .accessibilityElement(children: .combine)
        .accessibilityAddTraits(.isHeader)
    }
}
