"""Morning Radio: a bouncy lo-fi platformer tune in C major, 112 BPM, 16 bars.

A shuffled, brushy beat, a stepped triangle bass bouncing between roots and fifths,
a ukulele chopping on the off-beats and a playful lead on marimba doubled by a soft
square wave. The second half adds a harmony line and little coin-like sparkles. The
whole band goes through a small AM radio: squeezed to 300 Hz to 5 kHz, a bit driven
and wobbly, with crackle on top. For sunny early levels.
"""
from lofi import Song, dsp, inst

TRACK = {"title": "Morning Radio", "title_ko": "아침 라디오", "style": "Lo-fi platformer",
         "bpm": 112, "bars": 16, "key": "C major"}

# One bar per chord: (bass root, ukulele shape)
CHORDS = [
    ("C2", ("G4", "C4", "E4", "C5")),    # C
    ("A1", ("A4", "C4", "E4", "A4")),    # Am
    ("D2", ("A4", "D4", "F4", "C5")),    # Dm7
    ("G1", ("G4", "B3", "D4", "F4")),    # G7
    ("F2", ("A4", "C4", "F4", "A4")),    # F
    ("E2", ("G4", "B3", "E4", "G4")),    # Em
    ("D2", ("A4", "D4", "F4", "A4")),    # Dm
    ("G1", ("G4", "B3", "D4", "F4")),    # G7
]

# The lead, eight bars: (bar, step, note, length in steps)
TUNE = [
    (0, 0, "E5", 2), (0, 2, "G5", 2), (0, 4, "C6", 3), (0, 8, "B5", 2), (0, 10, "G5", 2), (0, 12, "E5", 4),
    (1, 0, "A5", 2), (1, 2, "G5", 2), (1, 4, "E5", 2), (1, 6, "C5", 2), (1, 8, "D5", 4), (1, 12, "E5", 2), (1, 14, "G5", 2),
    (2, 0, "F5", 2), (2, 2, "A5", 2), (2, 4, "C6", 2), (2, 6, "A5", 2), (2, 8, "F5", 2), (2, 10, "D5", 2), (2, 12, "F5", 4),
    (3, 0, "G5", 4), (3, 4, "F5", 2), (3, 6, "D5", 2), (3, 8, "B4", 4), (3, 12, "D5", 2), (3, 14, "F5", 2),
    (4, 0, "A5", 2), (4, 2, "C6", 2), (4, 4, "A5", 2), (4, 6, "F5", 2), (4, 8, "G5", 4), (4, 12, "A5", 4),
    (5, 0, "G5", 2), (5, 2, "B5", 2), (5, 4, "G5", 2), (5, 6, "E5", 2), (5, 8, "F5", 4), (5, 12, "G5", 4),
    (6, 0, "F5", 2), (6, 2, "E5", 2), (6, 4, "D5", 2), (6, 6, "F5", 2), (6, 8, "A5", 2), (6, 10, "G5", 2), (6, 12, "F5", 2), (6, 14, "D5", 2),
    (7, 0, "G5", 2), (7, 2, "F5", 2), (7, 4, "D5", 2), (7, 6, "B4", 2), (7, 8, "C5", 2), (7, 10, "D5", 2), (7, 12, "G5", 4),
]

# Second-half harmony a third or so under the tune, on the beat only: (bar, step, note)
HARMONY = [
    (0, 0, "C5"), (0, 4, "E5"), (0, 8, "G5"), (0, 12, "C5"), (1, 0, "E5"), (1, 4, "C5"), (1, 8, "B4"), (1, 12, "C5"),
    (2, 0, "D5"), (2, 4, "F5"), (2, 8, "D5"), (2, 12, "A4"), (3, 0, "D5"), (3, 4, "B4"), (3, 8, "G4"), (3, 12, "B4"),
    (4, 0, "F5"), (4, 4, "F5"), (4, 8, "E5"), (4, 12, "F5"), (5, 0, "E5"), (5, 4, "E5"), (5, 8, "D5"), (5, 12, "E5"),
    (6, 0, "D5"), (6, 4, "D5"), (6, 8, "F5"), (6, 12, "A4"), (7, 0, "D5"), (7, 4, "B4"), (7, 8, "A4"), (7, 12, "B4"),
]


def build():
    song = Song(bpm=TRACK["bpm"], bars=TRACK["bars"], swing=0.64, seed=61)
    rng = song.rng
    step = song.step_s

    def seed():
        return int(rng.integers(1_000_000))

    kits = {
        "kick": [inst.kick(seed=s, decay=0.15) for s in range(2)],
        "brush": [inst.brush(seed=s) for s in range(4)],
        "hat": [inst.hat(seed=s) for s in range(4)],
        "rim": [inst.rim(seed=s) for s in range(2)],
    }

    def hit(bus, kit, bar, st, vel, gain, pan_to=0.0, jitter=0.0):
        t = song.at(bar, st, jitter_ms=jitter)
        sounds = kits[kit]
        song.add(bus, sounds[rng.integers(len(sounds))], t, gain * vel * rng.uniform(0.9, 1.0), pan_to)
        return t

    for bar in range(song.bars):
        last = bar == song.bars - 1
        for st, vel in ((0, 1.0), (8, 0.85)) + (((14, 0.5),) if bar % 2 else ()):
            hit("drums", "kick", bar, st, vel, 1.0, jitter=2)
        for st in (4, 12):
            hit("drums", "brush", bar, st, 0.9, 0.9, jitter=4)
        for st in range(0, 16, 2):
            hit("drums", "brush", bar, st + 1, 0.25, 0.45, pan_to=0.2, jitter=4)
            hit("drums", "hat", bar, st, 0.35, 0.18, pan_to=-0.2, jitter=3)
        if last:
            for st, vel in ((10, 0.5), (11, 0.6), (13, 0.7), (14, 0.8), (15, 0.9)):
                hit("drums", "rim", bar, st, vel, 0.3, pan_to=-0.2, jitter=2)

    for bar in range(song.bars):
        root, shape = CHORDS[bar % len(CHORDS)]
        r = dsp.note(root)
        # Root, fifth, octave, fifth on the beats with a little pickup into the next bar
        for st, interval in ((0, 0), (4, 7), (8, 12), (12, 7)):
            freq = dsp.hz(r + 12 + interval)
            gate = step * 3.2
            n = dsp.samples(gate)
            tone = dsp.stepped_triangle(freq * dsp.np.ones(n)) * dsp.envelope(n, 0.003, 0.2, 0.8, 0.03, gate)
            song.add("bass", tone, song.at(bar, st), 0.45)
        for st in (2, 6, 10, 14):
            chop = inst.strum_guitar(shape, step * 1.1, down=st % 4 == 2, vel=0.8, seed=seed(), spread=0.006,
                                     brightness=0.5, decay=1.0)
            song.add("uke", chop, song.at(bar, st, jitter_ms=3), 1.0, pan_to=0.3)

    for half in (0, 8):
        for b, st, name, length in TUNE:
            gate = length * step * 0.9
            t = song.at(half + b, st, jitter_ms=3)
            song.add("lead", inst.marimba(name, gate, vel=0.9), t, 0.22, pan_to=-0.1)
            song.add("lead", inst.chip(name, gate, vel=0.6, duty=0.5, vibrato=0.6), t, 0.14, pan_to=0.1)
    for b, st, name in HARMONY:
        song.add("harmony", inst.marimba(name, step * 3, vel=0.7), song.at(8 + b, st, jitter_ms=3), 0.3, pan_to=0.4)
    # A little sparkle at the end of each phrase in the second half
    for bar in (11, 15):
        song.add("harmony", inst.chip_arp(("C6", "E6", "G6", "C7"), step * 3, 0.03, vel=0.5), song.at(bar, 12), 0.2)

    n = song.length
    bus = {name: song.bus(name) for name in ("drums", "bass", "uke", "lead", "harmony")}
    drums = dsp.saturate(bus["drums"], 1.3)
    bass = dsp.on_loop(bus["bass"], lambda s: dsp.lowpass(s, 2500))
    uke = dsp.on_loop(bus["uke"], lambda s: dsp.highpass(s, 250))
    lead = bus["lead"]
    harmony = bus["harmony"]
    echo = dsp.loop_convolve(lead + harmony, dsp.delay_ir(2 * step, feedback=0.25, damping=3000)) * 0.15
    band = drums + bass + uke + lead + harmony + echo
    room = dsp.loop_convolve(band, dsp.reverb_ir(0.9, brightness=4000)) * 0.06

    # The kitchen radio: a narrow, slightly driven speaker that wobbles a little
    def speaker(x):
        return dsp.on_loop(x, lambda s: dsp.lowpass(dsp.highpass(s, 300, order=3), 5000, order=3))

    radio = dsp.tape_wobble(dsp.saturate(speaker(band + room) * 1.6, 1.8), wow_hz=0.3, wow_ms=0.6, flutter_ms=0.08)
    static = inst.vinyl(n, seed=15, amount=1.2)

    # Each part through the speaker on its own, for checking the balance
    parts = {name: speaker(x) for name, x in
             {"drums": drums, "bass": bass, "uke": uke, "lead": lead, "harmony": harmony, "echo": echo, "room": room}.items()}
    parts["static"] = static
    return dsp.master(radio + static), parts
