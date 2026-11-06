import SwiftUI

/// Which folder the tapes come from, and anything that's gone wrong.
struct ShelfFooter: View {
    let folder: URL
    let problem: String?
    let choose: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(problem ?? "")
                .font(.label(11, relativeTo: .caption))
                .foregroundStyle(Palette.sakuraDeep)
                .opacity(problem == nil ? 0 : 1)
            HStack {
                Button(folder.lastPathComponent, systemImage: "folder", action: choose)
                    .buttonStyle(StickerButtonStyle())
                    .font(.label(11, relativeTo: .caption))
                    .help(folder.path(percentEncoded: false))
                Spacer()
                Text("(=^･ω･^=)")
                    .font(.label(13))
                    .foregroundStyle(Palette.ink)
                    .accessibilityHidden(true)
            }
        }
    }
}
