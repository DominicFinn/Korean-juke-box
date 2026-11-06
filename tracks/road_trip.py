"""Road Trip: sunny lo-fi folk pop in D major, 116 BPM, 16 bars.

Double-tracked strummed guitars driving down-down-up-up-down-up, a bouncy bass,
claps on two and four and a whistled tune in the second half. Upbeat but still
dusty round the edges, for open roads and overworld maps.
"""
from lofi import Song, dsp, inst

TRACK = {"title": "Road Trip", "title_ko": "드라이브 가는 길", "style": "Lo-fi folk pop",
         "bpm": 116, "bars": 16, "key": "D major"}

# One bar per chord: (bass root, guitar shape low to high)
CHORDS = [
    ("D2", ("D3", "A3", "D4", "F#4")),                 # D
    ("F#2", ("F#2", "C#3", "F#3", "A3", "C#4", "F#4")),  # F#m
    ("G2", ("G2", "B2", "D3", "G3", "B3", "G4")),       # G
    ("A2", ("A2", "E3", "A3", "C#4", "E4")),            # A
]

# Down, down-up, up-down-up on the 8ths: (step, downstroke, velocity)
STRUM = [(0, True, 0.95), (4, True, 0.8), (6, False, 0.55), (10, False, 0.6), (12, True, 0.8), (14, False, 0.55)]

# (step, interval above the root, length in steps)
BASS = [(0, 0, 3), (4, 12, 1.5), (6, 7, 1.5), (8, 0, 2.5), (11, 0, 1), (12, 7, 1.5), (14, 12, 1.5)]

# Whistled tune for bars 8 to 15: (bar, step, note, length in steps)
WHISTLE = [
    (0, 0, "F#5", 3), (0, 3, "A5", 1), (0, 4, "A5", 2), (0, 6, "B5", 2), (0, 8, "A5", 4), (0, 12, "F#5", 2), (0, 14, "E5", 2),
    (1, 0, "F#5", 6), (1, 6, "E5", 2), (1, 8, "C#5", 4),
    (2, 0, "D5", 2), (2, 2, "E5", 2), (2, 4, "G5", 4), (2, 8, "F#5", 2), (2, 10, "E5", 2), (2, 12, "D5", 4),
    (3, 0, "E5", 6), (3, 6, "C#5", 2), (3, 8, "A4", 4),
    (4, 0, "A5", 2), (4, 2, "F#5", 2), (4, 4, "A5", 2), (4, 6, "B5", 2), (4, 8, "D6", 4), (4, 12, "B5", 2), (4, 14, "A5", 2),
    (5, 0, "A5", 4), (5, 4, "F#5", 2), (5, 6, "E5", 2), (5, 8, "F#5", 6),
    (6, 0, "G5", 2), (6, 2, "F#5", 2), (6, 4, "E5", 2), (6, 6, "D5", 2), (6, 8, "B4", 4), (6, 12, "D5", 4),
    (7, 0, "E5", 8), (7, 12, "A4", 2), (7, 14, "C#5", 2),
]


def build():
    song = Song(bpm=TRACK["bpm"], bars=TRACK["bars"], swing=0.54, seed=31)
    rng = song.rng
    step = song.step_s

    def seed():
        return int(rng.integers(1_000_000))

    kits = {
        "kick": [inst.kick(seed=s, decay=0.18) for s in range(2)],
        "clap": [inst.clap(seed=s) for s in range(3)],
        "hat": [inst.hat(seed=s) for s in range(4)],
        "shaker": [inst.shaker(seed=s) for s in range(4)],
    }

    def hit(bus, kit, bar, st, vel, gain, pan_to=0.0, jitter=0.0):
        t = song.at(bar, st, jitter_ms=jitter)
        sounds = kits[kit]
        song.add(bus, sounds[rng.integers(len(sounds))], t, gain * vel * rng.uniform(0.92, 1.0), pan_to)
        return t

    kick_hits = []
    for bar in range(song.bars):
        stomp = bar >= 8
        last = bar == song.bars - 1
        kicks = [(0, 1.0), (8, 0.95)] + ([(4, 0.7), (12, 0.7)] if stomp else [(10, 0.6)])
        for st, vel in kicks:
            t = hit("kick", "kick", bar, st, vel, 0.85, jitter=2)
            if vel > 0.9:
                kick_hits.append(dsp.samples(t))
        claps = [(4, 1.0), (12, 1.0)]
        if last:
            claps += [(13, 0.45), (14, 0.6), (15, 0.75)]
        for st, vel in claps:
            hit("clap", "clap", bar, st, vel, 0.5, jitter=3)
        for st in range(0, 16, 2):
            hit("hats", "hat", bar, st, 0.5 if st % 4 == 2 else 0.3, 0.13, pan_to=0.3, jitter=3)
        for st in range(16):
            hit("hats", "shaker", bar, st, 0.3 if st % 2 else 0.2, 0.1, pan_to=-0.35, jitter=4)

    for bar in range(song.bars):
        root, shape = CHORDS[bar % len(CHORDS)]
        r = dsp.note(root)
        # Two guitars, one each side, strummed by slightly different hands
        for side, pan_to in ((0, -0.6), (1, 0.6)):
            for i, (st, down, vel) in enumerate(STRUM):
                next_st = STRUM[i + 1][0] if i + 1 < len(STRUM) else 16
                gate = (next_st - st) * step
                strings = shape if down else shape[-4:]
                sound = inst.strum_guitar(strings, gate, down=down, vel=vel, seed=seed(),
                                          spread=0.012 if down else 0.008, brightness=0.6)
                song.add("guitar", sound, song.at(bar, st, jitter_ms=5) + side * 0.006, 0.8, pan_to=pan_to)
        for st, interval, length in BASS:
            song.add("bass", inst.bass(r + interval, length * step * 0.85), song.at(bar, st), 0.4)

    for b, st, name, length in WHISTLE:
        note = inst.flute(name, length * step * 0.95, vel=0.8, seed=seed())
        song.add("lead", note, song.at(8 + b, st, jitter_ms=4), 0.22, pan_to=0.1)

    song.add("fx", inst.crash(seed=3), song.at(0), 0.1, pan_to=0.3)
    song.add("fx", inst.crash(seed=4), song.at(8), 0.1, pan_to=-0.3)
    rise = inst.swell(4 * step, seed=5)
    song.add("fx", rise, song.at(16) - len(rise) / dsp.SR, 0.06)

    n = song.length
    bus = {name: song.bus(name) for name in ("kick", "clap", "hats", "guitar", "bass", "lead", "fx")}
    drums = dsp.on_loop(dsp.saturate(bus["kick"] + bus["clap"] + bus["hats"], 1.4), lambda s: dsp.lowpass(s, 9000))
    bass = dsp.on_loop(bus["bass"], lambda s: dsp.lowpass(s, 1400)) * dsp.duck(n, kick_hits, 0.35, 0.08)
    guitar = dsp.on_loop(bus["guitar"], lambda s: dsp.lowpass(dsp.highpass(s, 140), 6500))
    guitar = dsp.tape_wobble(guitar, wow_ms=0.6) * dsp.duck(n, kick_hits, 0.15, 0.1)
    lead = dsp.tape_wobble(dsp.on_loop(bus["lead"], lambda s: dsp.highpass(s, 300)), wow_ms=0.6)
    echo = dsp.loop_convolve(lead, dsp.delay_ir(3 * step, feedback=0.3, damping=3000)) * 0.2
    sends = guitar * 0.15 + lead * 0.35 + bus["clap"] * 0.15 + bus["fx"] * 0.5
    verb = dsp.loop_convolve(sends, dsp.reverb_ir(1.8, brightness=5000)) * 0.3

    parts = {"drums": drums, "bass": bass, "guitar": guitar, "lead": lead, "fx": bus["fx"],
             "echo": echo, "reverb": verb, "vinyl": inst.vinyl(n, seed=6, amount=0.8)}
    return dsp.master(sum(parts.values())), parts
