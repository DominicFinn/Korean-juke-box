"""Konbini 3am: slow lo-fi hip hop in D dorian, 80 BPM, 16 bars.

Swung boom-bap under jazzy electric piano (Dm9, G13, Cmaj9, A7b9), an upright bass
walking between roots and rain on the shop window. The second eight bars add a
nylon guitar figure, and the last beat drops out before the loop comes round.
"""
from lofi import Song, dsp, inst

TRACK = {"title": "Konbini 3am", "title_ko": "편의점 새벽 3시", "style": "Lo-fi hip hop",
         "bpm": 80, "bars": 16, "key": "D dorian"}

# Two bars per chord: (bass root, fifth above it, electric piano voicing)
CHORDS = [
    ("D2", "A2", ("F3", "A3", "C4", "E4")),   # Dm9
    ("G1", "D2", ("F3", "A3", "B3", "E4")),   # G13
    ("C2", "G2", ("E3", "G3", "B3", "D4")),   # Cmaj9
    ("A1", "E2", ("E3", "G3", "Bb3", "C#4")),  # A7b9
]

# (bar in chord, step, length in steps, velocity)
KEYS = [
    (0, 0, 6, 0.7), (0, 7, 2, 0.45), (0, 10, 5, 0.6),
    (1, 3, 3, 0.5), (1, 8, 6, 0.65), (1, 15, 1, 0.4),
]

# (bar in chord, step, note or role, length in steps)
BASS = [
    (0, 0, "root", 5), (0, 6, "fifth", 2), (0, 10, "root", 4),
    (1, 0, "root", 3), (1, 6, "octave", 2), (1, 10, "fifth", 3), (1, 14, "approach", 2),
]

# Nylon guitar figure for the second half: (bar in chord, step, note, length in steps)
GUITAR = {
    0: [(0, 2, "A4", 2), (0, 4, "C5", 2), (0, 6, "E5", 4), (1, 4, "D5", 2), (1, 6, "C5", 2), (1, 8, "A4", 6)],
    1: [(0, 2, "B4", 2), (0, 4, "D5", 2), (0, 6, "F5", 4), (1, 4, "E5", 2), (1, 6, "D5", 2), (1, 8, "B4", 6)],
    2: [(0, 2, "G4", 2), (0, 4, "B4", 2), (0, 6, "D5", 4), (1, 4, "E5", 2), (1, 6, "D5", 2), (1, 8, "B4", 6)],
    3: [(0, 2, "G4", 2), (0, 4, "Bb4", 2), (0, 6, "C#5", 4), (1, 4, "E5", 2), (1, 6, "D5", 2), (1, 8, "A4", 4)],
}

HATS = [0.55, 0.2, 0.35, 0.18, 0.5, 0.2, 0.35, 0.22, 0.55, 0.2, 0.35, 0.18, 0.5, 0.2, 0.35, 0.25]


def build():
    song = Song(bpm=TRACK["bpm"], bars=TRACK["bars"], swing=0.6, seed=23)
    rng = song.rng
    step = song.step_s

    def seed():
        return int(rng.integers(1_000_000))

    kits = {
        "kick": [inst.kick(seed=s, decay=0.26) for s in range(2)],
        "snare": [inst.dusty_snare(seed=s) for s in range(3)],
        "hat": [inst.hat(seed=s) for s in range(4)],
        "open": [inst.hat(open_=True, seed=s) for s in range(2)],
        "rim": [inst.rim(seed=s) for s in range(2)],
    }

    def hit(bus, kit, bar, st, vel, gain, pan_to=0.0, jitter=0.0):
        t = song.at(bar, st, jitter_ms=jitter)
        sounds = kits[kit]
        song.add(bus, sounds[rng.integers(len(sounds))], t, gain * vel * rng.uniform(0.92, 1.0), pan_to)
        return t

    kick_hits = []
    for bar in range(song.bars):
        last = bar == song.bars - 1
        kicks = [(0, 1.0), (10, 0.85)] + ([(7, 0.5)] if bar % 2 else [(11, 0.45)])
        for st, vel in kicks:
            if last and st >= 12:
                continue
            t = hit("kick", "kick", bar, st, vel, 0.9, jitter=2)
            if vel > 0.8:
                kick_hits.append(dsp.samples(t))
        snares = [(4, 1.0)] + ([] if last else [(12, 1.0)])
        if bar % 4 == 3 and not last:
            snares.append((15, 0.25))
        for st, vel in snares:
            hit("snare", "snare", bar, st, vel, 0.6, jitter=4)
        for st, vel in enumerate(HATS):
            if last and st >= 12:
                break
            hit("hats", "hat", bar, st, vel, 0.16, pan_to=0.25, jitter=5)
        if bar % 2 == 1 and not last:
            hit("hats", "open", bar, 14, 0.5, 0.12, pan_to=-0.2, jitter=3)
        if bar >= 8:
            hit("perc", "rim", bar, 7 if bar % 2 else 13, 0.35, 0.22, pan_to=-0.35, jitter=4)

    prev_bass = dsp.note("A1")
    for slot in range(song.bars // 2):
        root, fifth, voicing = CHORDS[slot % len(CHORDS)]
        r = dsp.note(root)
        next_root = dsp.note(CHORDS[(slot + 1) % len(CHORDS)][0])
        roles = {"root": r, "fifth": dsp.note(fifth), "octave": r + 12, "approach": next_root + 1}
        first_bar = slot * 2

        for b, st, length, vel in KEYS:
            stab = inst.strum(inst.epiano, voicing, length * step, vel, spread=0.014, seed=seed())
            song.add("keys", stab, song.at(first_bar + b, st, jitter_ms=8), 0.25)

        for b, st, role, length in BASS:
            m = roles[role]
            song.add("bass", inst.upright(m, length * step * 0.9, vel=0.9), song.at(first_bar + b, st, jitter_ms=4), 0.6)
            prev_bass = m

        if slot >= 4:
            for b, st, name, length in GUITAR[slot % len(CHORDS)]:
                note = inst.pluck(name, length * step, vel=0.7, seed=seed(), brightness=0.25, decay=1.6)
                song.add("guitar", note, song.at(first_bar + b, st, jitter_ms=6), 0.9, pan_to=0.3)

    rise = inst.swell(4 * step, seed=4)
    song.add("fx", rise, song.at(16) - len(rise) / dsp.SR, 0.05)

    n = song.length
    bus = {name: song.bus(name) for name in ("kick", "snare", "hats", "perc", "bass", "keys", "guitar", "fx")}
    drums = bus["kick"] + bus["snare"] + bus["hats"] + bus["perc"]
    drums = dsp.on_loop(dsp.saturate(drums, 1.5), lambda s: dsp.lowpass(s, 7500))
    bass = dsp.on_loop(bus["bass"], lambda s: dsp.lowpass(s, 900)) * dsp.duck(n, kick_hits, 0.3, 0.1)
    keys = dsp.on_loop(bus["keys"], lambda s: dsp.lowpass(dsp.highpass(s, 120), 3600))
    keys = dsp.tape_wobble(keys, wow_ms=1.2) * dsp.duck(n, kick_hits, 0.2, 0.15)
    guitar = dsp.tape_wobble(dsp.on_loop(bus["guitar"], lambda s: dsp.lowpass(dsp.highpass(s, 200), 5000)), wow_ms=1.2)
    echo = dsp.loop_convolve(guitar, dsp.delay_ir(3 * step, feedback=0.35, damping=2500)) * 0.25
    sends = keys * 0.3 + guitar * 0.4 + bus["snare"] * 0.1 + bus["perc"] * 0.2 + bus["fx"] * 0.5 + echo * 0.3
    verb = dsp.loop_convolve(sends, dsp.reverb_ir(2.2, brightness=4500)) * 0.35
    weather = inst.rain(n, seed=8, amount=1.0) + inst.vinyl(n, seed=9, amount=1.3)

    parts = {"drums": drums, "bass": bass, "keys": keys, "guitar": guitar, "fx": bus["fx"],
             "echo": echo, "reverb": verb, "rain": weather}
    return dsp.master(sum(parts.values())), parts
