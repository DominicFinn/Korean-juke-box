"""Sakura Drift: Japanese lo-fi in D minor, 88 BPM, 16 bars.

A koto picks out a tune in the in scale (D, Eb, G, A, Bb) over a soft half-time beat
and a warm pad. The second half adds a low koto walking the roots and a breathy
bamboo flute answering the tune. Calm, for villages, hubs and save rooms.
"""
from lofi import Song, dsp, inst

TRACK = {"title": "Sakura Drift", "title_ko": "벚꽃 바람", "style": "Japanese lo-fi",
         "bpm": 88, "bars": 16, "key": "D minor (in scale)"}

# Two bars per chord: (low koto root, pad voicing)
CHORDS = [
    ("D3", ("D3", "A3", "C4", "F4")),     # Dm7
    ("Eb3", ("Eb3", "G3", "Bb3", "D4")),  # Ebmaj7
    ("G2", ("G3", "Bb3", "D4", "F4")),    # Gm7
    ("Bb2", ("Bb2", "F3", "A3", "D4")),   # Bbmaj7
]

# Koto tune, eight bars: (bar, step, note, length in steps). Rolled chords are lists.
KOTO = [
    (0, 0, "A4", 4), (0, 4, "Bb4", 2), (0, 6, "A4", 2), (0, 8, "G4", 8),
    (1, 0, "D5", 3), (1, 3, "Eb5", 1), (1, 4, "D5", 4), (1, 8, "A4", 4), (1, 12, "G4", 4),
    (2, 0, "G4", 2), (2, 2, "Bb4", 2), (2, 4, "D5", 4), (2, 8, "Eb5", 2), (2, 10, "D5", 2), (2, 12, "Bb4", 4),
    (3, 0, ["Eb4", "G4", "Bb4", "D5"], 8), (3, 8, "A4", 4), (3, 12, "Bb4", 4),
    (4, 0, "D5", 2), (4, 2, "Bb4", 2), (4, 4, "G4", 4), (4, 8, "A4", 2), (4, 10, "Bb4", 2), (4, 12, "D5", 4),
    (5, 0, "Eb5", 4), (5, 4, "D5", 4), (5, 8, "Bb4", 8),
    (6, 0, "A4", 4), (6, 4, "G4", 2), (6, 6, "Eb4", 2), (6, 8, "D4", 8),
    (7, 0, ["D4", "G4", "A4", "D5"], 8), (7, 12, "A4", 2), (7, 14, "Bb4", 2),
]

# Flute answers in the second half: (bar, step, note, length in steps)
FLUTE = [
    (1, 8, "A5", 8), (3, 8, "G5", 4), (3, 12, "A5", 4), (5, 8, "Bb5", 4), (5, 12, "A5", 4),
    (6, 8, "G5", 4), (6, 12, "D5", 4), (7, 4, "D5", 12),
]

# Low koto pattern per bar: (step, interval above the root, length in steps)
LOW = [(0, 0, 6), (6, 7, 2), (8, 12, 4), (12, 7, 4)]


def build():
    song = Song(bpm=TRACK["bpm"], bars=TRACK["bars"], swing=0.58, seed=71)
    rng = song.rng
    step = song.step_s

    def seed():
        return int(rng.integers(1_000_000))

    kits = {
        "kick": [inst.kick(seed=s, decay=0.25) for s in range(2)],
        "snare": [inst.dusty_snare(seed=s) for s in range(2)],
        "rim": [inst.rim(seed=s) for s in range(2)],
        "shaker": [inst.shaker(seed=s) for s in range(4)],
        "hat": [inst.hat(seed=s) for s in range(4)],
    }

    def hit(bus, kit, bar, st, vel, gain, pan_to=0.0, jitter=0.0):
        t = song.at(bar, st, jitter_ms=jitter)
        sounds = kits[kit]
        song.add(bus, sounds[rng.integers(len(sounds))], t, gain * vel * rng.uniform(0.9, 1.0), pan_to)
        return t

    kick_hits = []
    for bar in range(song.bars):
        # Half-time: kick on one, snare on three
        kick_hits.append(dsp.samples(hit("drums", "kick", bar, 0, 1.0, 0.5, jitter=2)))
        hit("drums", "kick", bar, 10 if bar % 2 else 11, 0.6, 0.5, jitter=3)
        hit("drums", "snare", bar, 8, 0.9, 0.3, jitter=4)
        for st in range(0, 16, 2):
            hit("drums", "shaker", bar, st, 0.35 if st % 4 else 0.2, 0.12, pan_to=0.35, jitter=5)
        if bar >= 8:
            for st in (3, 7, 11, 15):
                hit("drums", "hat", bar, st, 0.25, 0.1, pan_to=-0.3, jitter=4)
        if bar % 4 == 3:
            hit("drums", "rim", bar, 14, 0.35, 0.25, pan_to=-0.3, jitter=3)

    for slot in range(song.bars // 2):
        root, voicing = CHORDS[slot % len(CHORDS)]
        song.add("pad", inst.pad(voicing, 32 * step - 0.3, cutoff=900, seed=seed()), song.at(slot * 2), 0.2)
        if slot >= 4:
            r = dsp.note(root) - 12
            for b in (0, 1):
                for st, interval, length in LOW:
                    note = inst.pluck(r + interval, length * step, vel=0.8, seed=seed(), brightness=0.35, decay=3.0)
                    song.add("low", note, song.at(slot * 2 + b, st, jitter_ms=4), 0.5, pan_to=-0.2)

    for half in (0, 8):
        for b, st, name, length in KOTO:
            notes = name if isinstance(name, list) else [name]
            for i, m in enumerate(notes):
                # Rolled chords spread their notes across a sixteenth
                t = song.at(half + b, st, jitter_ms=5) + i * step * 0.3
                note = inst.pluck(m, length * step, vel=0.85 - 0.05 * i, seed=seed(), brightness=0.5, decay=2.8)
                song.add("koto", note, t, 0.8, pan_to=0.15)
    for b, st, name, length in FLUTE:
        song.add("flute", inst.flute(name, length * step, vel=0.8, seed=seed()), song.at(8 + b, st, jitter_ms=5), 0.15,
                 pan_to=-0.15)

    n = song.length
    bus = {name: song.bus(name) for name in ("drums", "pad", "low", "koto", "flute")}
    drums = dsp.on_loop(dsp.saturate(bus["drums"], 1.3), lambda s: dsp.lowpass(s, 7000))
    pad = dsp.tape_wobble(bus["pad"], wow_ms=1.0) * dsp.duck(n, kick_hits, 0.3, 0.25)
    low = dsp.on_loop(bus["low"], lambda s: dsp.lowpass(s, 2500))
    koto = dsp.tape_wobble(dsp.on_loop(bus["koto"], lambda s: dsp.lowpass(dsp.highpass(s, 180), 6000)), wow_ms=0.7)
    flute = dsp.tape_wobble(bus["flute"], wow_ms=0.7)
    echo = dsp.loop_convolve(koto + flute, dsp.delay_ir(3 * step, feedback=0.3, damping=2800)) * 0.18
    sends = koto * 0.35 + flute * 0.45 + pad * 0.3 + low * 0.15 + echo * 0.4
    verb = dsp.loop_convolve(sends, dsp.reverb_ir(2.6, brightness=5000)) * 0.35

    parts = {"drums": drums, "pad": pad, "low": low, "koto": koto, "flute": flute, "echo": echo,
             "reverb": verb, "vinyl": inst.vinyl(n, seed=16, amount=0.7)}
    return dsp.master(sum(parts.values())), parts
