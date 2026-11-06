import SwiftUI

/// A comic panel: flat fill and a heavy ink border.
struct MangaPanel: ViewModifier {
    var fill: Color

    func body(content: Content) -> some View {
        content
            .background(fill)
            .clipShape(.rect)
            .overlay {
                Rectangle().strokeBorder(Palette.ink, lineWidth: 3)
            }
    }
}

extension View {
    func mangaPanel(fill: Color = Palette.paper) -> some View {
        modifier(MangaPanel(fill: fill))
    }
}
