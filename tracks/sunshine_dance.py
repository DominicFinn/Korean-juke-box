"""Sunshine Dance: lo-fi afrobeats in A major, 108 BPM, 16 bars.

A bouncing three-three-two kick, busy shakers and congas, and a clean highlife
guitar picking out the chords in sixteenths. The second half adds bright horn
stabs and a short horn tune of its own. Joyful and danceable, for festivals,
celebrations and victory screens.
"""
from lofi import Song, dsp, inst

TRACK = {"title": "Sunshine Dance", "title_ko": "햇살 댄스", "style": "Lo-fi afrobeats",
         "bpm": 108, "bars": 16, "key": "A major"}

# One bar per chord: (bass root, guitar figure over the 16ths, horn stab voicing)
CHORDS = [
    ("A1", ("E4", "A4", "C#5", "A4", "E5", "C#5", "A4", "C#5"), ("C#4", "E4", "A4")),     # A
    ("F#1", ("C#4", "F#4", "A4", "F#4", "C#5", "A4", "F#4", "A4"), ("C#4", "F#4", "A4")),  # F#m
    ("D2", ("D4", "F#4", "A4", "F#4", "D5", "A4", "F#4", "A4"), ("D4", "F#4", "A4")),     # D
    ("E2", ("E4", "G#4", "B4", "G#4", "E5", "B4", "G#4", "B4"), ("D4", "G#4", "B4")),     # E7
]

# Guitar picks on these 16ths, cycling through the chord's figure
PICKS = [0, 2, 3, 5, 6, 8, 10, 11, 13, 14]

# (step, interval above the root, length in steps)
BASS = [(0, 0, 2.5), (3, 0, 1), (6, 7, 2), (10, 0, 1.5), (12, 12, 1), (14, 7, 1.5)]

# Congas: (step, high drum, slap, velocity)
CONGAS = [(2, True, False, 0.6), (3, True, False, 0.45), (6, False, False, 0.7), (7, True, False, 0.4),
          (10, True, False, 0.55), (11, True, True, 0.7), (14, False, False, 0.65), (15, True, False, 0.4)]

# Horn tune for bars 12 to 15: (bar, step, note, length in steps)
HORNS = [
    (0, 0, "E5", 1.5), (0, 3, "E5", 1), (0, 6, "C#5", 2), (0, 10, "E5", 1.5), (0, 12, "F#5", 3),
    (1, 0, "E5", 1.5), (1, 3, "C#5", 1), (1, 6, "A4", 2), (1, 10, "B4", 1.5), (1, 12, "C#5", 3),
    (2, 0, "D5", 1.5), (2, 3, "F#5", 1), (2, 6, "A5", 2), (2, 10, "F#5", 1.5), (2, 12, "E5", 3),
    (3, 0, "E5", 1.5), (3, 3, "D5", 1), (3, 6, "B4", 2), (3, 8, "G#4", 2), (3, 12, "B4", 1.5), (3, 14, "C#5", 2),
]


def build():
    song = Song(bpm=TRACK["bpm"], bars=TRACK["bars"], swing=0.56, seed=51)
    rng = song.rng
    step = song.step_s

    def seed():
        return int(rng.integers(1_000_000))

    kits = {
        "kick": [inst.kick(seed=s, decay=0.2) for s in range(2)],
        "clap": [inst.clap(seed=s) for s in range(3)],
        "rim": [inst.rim(seed=s) for s in range(3)],
        "shaker": [inst.shaker(seed=s) for s in range(4)],
        "hat": [inst.hat(seed=s) for s in range(4)],
        "high": [inst.conga(high=True, seed=s) for s in range(3)],
        "low": [inst.conga(high=False, seed=s) for s in range(3)],
        "slap": [inst.conga(high=True, slap=True, seed=s) for s in range(3)],
    }

    def hit(bus, kit, bar, st, vel, gain, pan_to=0.0, jitter=0.0):
        t = song.at(bar, st, jitter_ms=jitter)
        sounds = kits[kit]
        song.add(bus, sounds[rng.integers(len(sounds))], t, gain * vel * rng.uniform(0.92, 1.0), pan_to)
        return t

    kick_hits = []
    for bar in range(song.bars):
        last = bar == song.bars - 1
        # Three-three-two across the bar, with a pickup on alternate bars
        kicks = [(0, 1.0), (6, 0.85), (12, 0.9)] + ([(14, 0.6)] if bar % 2 else [])
        for st, vel in kicks:
            t = hit("kick", "kick", bar, st, vel, 0.7, jitter=2)
            if vel > 0.8:
                kick_hits.append(dsp.samples(t))
        for st in (4, 12):
            hit("clap", "clap", bar, st, 0.8, 0.4, jitter=3)
        for st in (3, 7, 10) if bar % 2 else (3, 10, 14):
            hit("perc", "rim", bar, st, 0.4, 0.25, pan_to=-0.4, jitter=3)
        for st in range(16):
            hit("perc", "shaker", bar, st, 0.45 if st % 4 == 2 else 0.25, 0.14, pan_to=0.4, jitter=4)
        for st in (2, 6, 10, 14):
            hit("hats", "hat", bar, st, 0.4, 0.1, pan_to=0.2, jitter=3)
        if bar >= 4:
            for st, high, slap, vel in CONGAS:
                hit("congas", "slap" if slap else ("high" if high else "low"), bar, st, vel, 0.3,
                    pan_to=-0.25 if high else 0.15, jitter=5)
        if last:
            for st, vel in ((13, 0.5), (14, 0.65), (15, 0.8)):
                hit("congas", "slap", bar, st, vel, 0.35, jitter=3)

    for bar in range(song.bars):
        root, figure, stab_notes = CHORDS[bar % len(CHORDS)]
        r = dsp.note(root)
        for i, st in enumerate(PICKS):
            note = inst.pluck(figure[i % len(figure)], step * 1.6, vel=0.75 if st % 4 == 0 else 0.6,
                              seed=seed(), brightness=0.75, decay=1.2)
            song.add("guitar", note, song.at(bar, st, jitter_ms=3), 0.95, pan_to=0.45)
        for st, interval, length in BASS:
            song.add("bass", inst.bass(r + interval, length * step * 0.85), song.at(bar, st), 0.45)
        if bar >= 8:
            for st in (3, 10):
                stab = inst.strum(inst.brass, stab_notes, step * 1.2, 0.8, spread=0.003, seed=seed())
                song.add("horns", stab, song.at(bar, st, jitter_ms=3), 0.2, pan_to=-0.2)

    for b, st, name, length in HORNS:
        line = inst.strum(inst.brass, (name, dsp.note(name) - 12), length * step, 0.85, spread=0.0, seed=seed())
        song.add("horns", line, song.at(12 + b, st, jitter_ms=3), 0.26, pan_to=0.1)

    song.add("fx", inst.crash(seed=6), song.at(0), 0.1, pan_to=0.3)
    song.add("fx", inst.crash(seed=7), song.at(8), 0.1, pan_to=-0.3)

    n = song.length
    bus = {name: song.bus(name) for name in ("kick", "clap", "perc", "hats", "congas", "guitar", "bass", "horns", "fx")}
    drums = bus["kick"] + bus["clap"] + bus["perc"] + bus["hats"] + bus["congas"]
    drums = dsp.on_loop(dsp.saturate(drums, 1.4), lambda s: dsp.lowpass(s, 9000))
    bass = dsp.on_loop(bus["bass"], lambda s: dsp.lowpass(s, 1200)) * dsp.duck(n, kick_hits, 0.35, 0.08)
    guitar = dsp.tape_wobble(dsp.on_loop(bus["guitar"], lambda s: dsp.lowpass(dsp.highpass(s, 250), 7000)), wow_ms=0.5)
    horns = dsp.tape_wobble(dsp.on_loop(bus["horns"], lambda s: dsp.lowpass(dsp.highpass(s, 200), 6000)), wow_ms=0.5)
    echo = dsp.loop_convolve(guitar, dsp.delay_ir(3 * step, feedback=0.25, damping=3000)) * 0.15
    sends = guitar * 0.15 + horns * 0.3 + bus["clap"] * 0.15 + bus["congas"] * 0.15 + bus["fx"] * 0.4
    verb = dsp.loop_convolve(sends, dsp.reverb_ir(1.6, brightness=5500)) * 0.3

    parts = {"drums": drums, "bass": bass, "guitar": guitar, "horns": horns, "fx": bus["fx"],
             "echo": echo, "reverb": verb, "vinyl": inst.vinyl(n, seed=14, amount=0.7)}
    return dsp.master(sum(parts.values())), parts
