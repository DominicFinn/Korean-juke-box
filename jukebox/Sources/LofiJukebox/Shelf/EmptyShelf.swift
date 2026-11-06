import SwiftUI

struct EmptyShelf: View {
    var body: some View {
        VStack(spacing: 10) {
            Text("(=｀ω´=)")
                .font(.label(28))
            Text("아직 테이프가 없어요")
                .font(.serif(15))
            Text("render.py로 루프를 만들면 여기에 나타나요.")
                .font(.label(11, relativeTo: .caption))
                .multilineTextAlignment(.center)
                .opacity(0.75)
        }
        .foregroundStyle(Palette.ink)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding()
    }
}
