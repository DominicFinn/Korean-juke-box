import SwiftUI

extension Font {
    /// Apple SD Gothic Neo: clean and friendly, for most text.
    static func label(_ size: Double, relativeTo style: Font.TextStyle = .body) -> Font {
        .custom("AppleSDGothicNeo-Medium", size: size, relativeTo: style)
    }

    /// Heavy Apple SD Gothic Neo, for headings and comic sound effects.
    static func heavy(_ size: Double, relativeTo style: Font.TextStyle = .title) -> Font {
        .custom("AppleSDGothicNeo-Heavy", size: size, relativeTo: style)
    }

    /// AppleMyungjo, a serif for episode captions and handwritten-looking tape labels.
    static func serif(_ size: Double, relativeTo style: Font.TextStyle = .body) -> Font {
        .custom("AppleMyungjo", size: size, relativeTo: style)
    }
}
