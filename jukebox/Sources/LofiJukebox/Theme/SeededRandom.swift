/// SplitMix64. The city is drawn from a fixed seed so it looks the same every frame.
struct SeededRandom: RandomNumberGenerator {
    private var state: UInt64

    init(seed: UInt64) {
        state = seed
    }

    mutating func next() -> UInt64 {
        state &+= 0x9E37_79B9_7F4A_7C15
        var z = state
        z = (z ^ (z >> 30)) &* 0xBF58_476D_1CE4_E5B9
        z = (z ^ (z >> 27)) &* 0x94D0_49BB_1331_11EB
        return z ^ (z >> 31)
    }

    /// A repeatable value from 0 to 1 for up to four numbers.
    static func noise(_ a: UInt64, _ b: UInt64 = 0, _ c: UInt64 = 0, _ d: UInt64 = 0) -> Double {
        var generator = SeededRandom(seed: (((0x5EED &* 31 &+ a) &* 31 &+ b) &* 31 &+ c) &* 31 &+ d)
        return Double(generator.next() >> 11) / Double(1 << 53)
    }
}
