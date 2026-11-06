import SwiftUI

/// How many times each tape plays before the jukebox moves on: ×2 번씩, "twice each".
struct PlaysStepper: View {
    @Binding var plays: Int

    var body: some View {
        HStack(spacing: 6) {
            Button("Fewer plays", systemImage: "minus", action: fewer)
                .disabled(plays <= Player.playRange.lowerBound)
            Text("×\(plays)")
                .font(.heavy(14, relativeTo: .body))
                .monospacedDigit()
                .frame(minWidth: 28)
            Button("More plays", systemImage: "plus", action: more)
                .disabled(plays >= Player.playRange.upperBound)
            Text("번씩")
                .font(.label(12))
                .padding(.leading, 4)
        }
        .buttonStyle(StickerButtonStyle(diameter: 24))
        .labelStyle(.iconOnly)
        .font(.system(size: 10, weight: .heavy))
        .foregroundStyle(Palette.ink)
        .accessibilityRepresentation {
            Stepper("Plays per tape: \(plays)", value: $plays, in: Player.playRange)
        }
    }

    private func fewer() {
        plays = max(Player.playRange.lowerBound, plays - 1)
    }

    private func more() {
        plays = min(Player.playRange.upperBound, plays + 1)
    }
}
