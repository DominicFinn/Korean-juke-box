import SwiftUI

/// The plays-per-tape stepper, switched off while a tape is set to loop.
struct PlaysControl: View {
    @Bindable var player: Player

    var body: some View {
        PlaysStepper(plays: $player.playsPerTrack)
            .disabled(player.repeatOne)
    }
}
