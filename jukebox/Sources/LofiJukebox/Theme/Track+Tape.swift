import SwiftUI

extension Track {
    /// Each tape gets a shell colour from its name, so it stays the same between launches.
    var tapeColor: Color {
        let total = id.unicodeScalars.reduce(0) { $0 + Int($1.value) }
        return Palette.tapes[total % Palette.tapes.count]
    }

    /// "130 BPM · F단조", or whichever parts are known.
    var details: String {
        var parts: [String] = []
        if bpm > 0 { parts.append("\(Int(bpm.rounded())) BPM") }
        if !key.isEmpty { parts.append(koreanKey) }
        return parts.joined(separator: " · ")
    }

    /// render.py writes keys in English, like "F minor". Korean says 단조 for minor and
    /// 장조 for major.
    private var koreanKey: String {
        key.replacing(" (in scale)", with: "")
            .replacing(" minor", with: "단조")
            .replacing(" major", with: "장조")
            .replacing(" dorian", with: " 도리안")
    }
}
