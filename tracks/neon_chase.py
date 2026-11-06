"""Neon Chase: lo-fi liquid drum and bass in E minor, 172 BPM, 32 bars.

A chopped, crunchy break with ghost snares, a deep sub under warm pads and electric
piano, and a plucked arpeggio running through it. The second sixteen bars bring in a
growling reese and a ride, and every eighth bar ends in a snare roll. Fast without
being harsh, for chases, races and boss phases.
"""
from lofi import Song, dsp, inst

TRACK = {"title": "Neon Chase", "title_ko": "네온 추격전", "style": "Lo-fi drum and bass",
         "bpm": 172, "bars": 32, "key": "E minor"}

# Four bars per chord: (sub root, pad voicing, arpeggio notes)
CHORDS = [
    ("E1", ("G3", "B3", "D4", "F#4"), ("E4", "G4", "B4", "D5", "F#5", "D5", "B4", "G4")),   # Em9
    ("C2", ("G3", "B3", "E4", "D4"), ("C4", "G4", "B4", "D5", "E5", "D5", "B4", "G4")),     # Cmaj9
    ("A1", ("G3", "C4", "E4", "B4"), ("A4", "C5", "E5", "G5", "B5", "G5", "E5", "C5")),     # Am9
    ("B1", ("A3", "D#4", "F#4", "B4"), ("B4", "D#5", "F#5", "A5", "B5", "A5", "F#5", "D#5")),  # B7
]

# Two-bar break: (step, kick, snare velocity or 0)
BREAK = [
    [(0, True, 0), (4, False, 1.0), (7, False, 0.3), (9, False, 0.25), (10, True, 0), (12, False, 1.0), (15, False, 0.3)],
    [(0, True, 0), (2, True, 0), (4, False, 1.0), (6, False, 0.25), (10, True, 0), (11, False, 0.3), (12, False, 1.0), (14, False, 0.35)],
]
HATS = [0.5, 0.15, 0.35, 0.15, 0.45, 0.15, 0.35, 0.2, 0.5, 0.15, 0.35, 0.15, 0.45, 0.2, 0.35, 0.25]

# Sub line per bar: (step, length in steps)
SUB = [(0, 6), (10, 4), (14, 2)]


def build():
    song = Song(bpm=TRACK["bpm"], bars=TRACK["bars"], swing=0.53, seed=81)
    rng = song.rng
    step = song.step_s

    def seed():
        return int(rng.integers(1_000_000))

    kits = {
        "kick": [inst.kick(seed=s, decay=0.14) for s in range(2)],
        "snare": [inst.break_snare(seed=s) for s in range(4)],
        "hat": [inst.hat(seed=s) for s in range(4)],
        "ride": [inst.ride(seed=s) for s in range(2)],
    }

    def hit(bus, kit, bar, st, vel, gain, pan_to=0.0, jitter=0.0):
        t = song.at(bar, st, jitter_ms=jitter)
        sounds = kits[kit]
        song.add(bus, sounds[rng.integers(len(sounds))], t, gain * vel * rng.uniform(0.9, 1.0), pan_to)
        return t

    kick_hits = []
    for bar in range(song.bars):
        roll = bar % 8 == 7
        for st, is_kick, snare in BREAK[bar % 2]:
            if roll and st >= 12:
                continue
            if is_kick:
                kick_hits.append(dsp.samples(hit("break", "kick", bar, st, 1.0, 0.9, jitter=1)))
            else:
                hit("break", "snare", bar, st, snare, 0.55, jitter=2)
        if roll:
            for st in range(12, 16):
                hit("break", "snare", bar, st, 0.4 + 0.15 * (st - 12), 0.55, jitter=1)
        for st, vel in enumerate(HATS):
            hit("break", "hat", bar, st, vel, 0.14, pan_to=0.3, jitter=2)
        if bar >= 16:
            for st in (0, 4, 8, 12):
                hit("ride", "ride", bar, st, 0.6 if st == 0 else 0.4, 0.12, pan_to=-0.35, jitter=2)

    for slot in range(song.bars // 4):
        root, voicing, arp = CHORDS[slot % len(CHORDS)]
        r = dsp.note(root)
        first_bar = slot * 4
        song.add("pad", inst.pad(voicing, 64 * step - 0.2, cutoff=1400, seed=seed()), song.at(first_bar), 0.3)
        for b in range(4):
            bar = first_bar + b
            for st, length in SUB:
                song.add("sub", inst.bass(r + 12, length * step * 0.9, vel=0.9), song.at(bar, st), 0.55)
            for st in range(0, 16, 2 if bar < 16 else 1):
                note = arp[(st // (2 if bar < 16 else 1)) % len(arp)]
                pluck = inst.pluck(note, step * 1.5, vel=0.6 if st % 4 else 0.75, seed=seed(), brightness=0.6, decay=1.0)
                song.add("arp", pluck, song.at(bar, st, jitter_ms=2), 0.6, pan_to=0.4 if st % 4 < 2 else -0.4)
            if b in (0, 2):
                stab = inst.strum(inst.epiano, voicing, 6 * step, 0.6, seed=seed())
                song.add("keys", stab, song.at(bar, 6 if b == 0 else 3, jitter_ms=4), 0.16)
            if bar >= 16:
                song.add("reese", inst.reese(r + 12, 15 * step, vel=0.8, seed=seed()), song.at(bar, 0), 0.5)

    song.add("fx", inst.crash(seed=8), song.at(0), 0.12, pan_to=0.3)
    song.add("fx", inst.crash(seed=9), song.at(16), 0.12, pan_to=-0.3)
    for end in (16, 32):
        rise = inst.swell(8 * step, seed=end)
        song.add("fx", rise, song.at(end) - len(rise) / dsp.SR, 0.07)

    n = song.length
    bus = {name: song.bus(name) for name in ("break", "ride", "sub", "reese", "pad", "keys", "arp", "fx")}
    # Crunch the break like a sampled loop
    drums = dsp.crush(dsp.saturate(bus["break"], 1.6), bits=12, hold=2) + bus["ride"]
    drums = dsp.on_loop(drums, lambda s: dsp.lowpass(dsp.highpass(s, 35), 9000))
    sub = dsp.on_loop(bus["sub"], lambda s: dsp.lowpass(s, 300)) * dsp.duck(n, kick_hits, 0.5, 0.08)
    reese = dsp.on_loop(bus["reese"], lambda s: dsp.lowpass(s, 2500)) * dsp.duck(n, kick_hits, 0.4, 0.1)
    pad = dsp.tape_wobble(bus["pad"]) * dsp.duck(n, kick_hits, 0.45, 0.12)
    keys = dsp.tape_wobble(dsp.on_loop(bus["keys"], lambda s: dsp.lowpass(dsp.highpass(s, 200), 4500)))
    arp = dsp.tape_wobble(dsp.on_loop(bus["arp"], lambda s: dsp.lowpass(dsp.highpass(s, 300), 6000)))
    echo = dsp.loop_convolve(arp, dsp.delay_ir(3 * step, feedback=0.4, damping=2500)) * 0.25
    sends = pad * 0.4 + keys * 0.3 + arp * 0.3 + echo * 0.3 + bus["fx"] * 0.5
    verb = dsp.loop_convolve(sends, dsp.reverb_ir(2.4, brightness=5000)) * 0.3

    parts = {"drums": drums, "sub": sub, "reese": reese, "pad": pad, "keys": keys, "arp": arp, "fx": bus["fx"],
             "echo": echo, "reverb": verb, "vinyl": inst.vinyl(n, seed=17, amount=0.7)}
    return dsp.master(sum(parts.values())), parts
