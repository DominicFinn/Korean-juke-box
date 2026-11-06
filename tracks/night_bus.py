"""Night Bus: lo-fi 2-step garage in F minor, 130 BPM, 16 bars.

Shuffled hats and a skippy 2-step kick under dusty electric piano stabs, a sub bass
that slides between chords and chopped 'ooh-ah' vocals. The second eight bars add a
shaker, busier keys and answer phrases in the vocal, so the loop has some shape to it
rather than repeating every two bars.
"""
from lofi import Song, dsp, inst

TRACK = {"title": "Night Bus", "title_ko": "심야버스", "style": "Lo-fi 2-step garage",
         "bpm": 130, "bars": 16, "key": "F minor"}

# Two bars per chord: bass root, intervals of its 3rd and 7th, electric piano voicing,
# and the notes the vocal can pick from (low to high).
CHORDS = [
    ("F2", 3, 10, ("Ab3", "C4", "Eb4", "G4"), ("G4", "Ab4", "C5", "Eb5", "F5")),   # Fm9
    ("Db2", 4, 11, ("Ab3", "C4", "Eb4", "F4"), ("F4", "Ab4", "C5", "Eb5", "F5")),  # Dbmaj9
    ("Bb1", 3, 10, ("Ab3", "C4", "Db4", "F4"), ("F4", "Ab4", "C5", "Db5", "F5")),  # Bbm9
    ("C2", 4, 10, ("Bb3", "Db4", "E4", "G4"), ("E4", "G4", "Bb4", "Db5", "E5")),   # C7b9
]

# (bar in chord, step, interval or role, length in steps, glide in from last note)
BASS = [
    (0, 0, 0, 2.5, True), (0, 3, 12, 0.75, False), (0, 6, 0, 1.5, False),
    (0, 10, 0, 2.5, False), (0, 14, "7th", 1.5, False),
    (1, 0, 0, 2.5, True), (1, 7, 7, 1.0, False), (1, 10, 0, 2.0, False),
    (1, 13, "3rd", 0.6, False), (1, 14, "approach", 2.0, False),
]

# (bar in chord, step, length in steps, velocity)
KEYS_A = [
    (0, 0, 3, 0.75), (0, 3, 1.5, 0.55), (0, 7, 2, 0.65), (0, 10, 4, 0.7),
    (1, 2, 2, 0.6), (1, 6, 1.5, 0.5), (1, 9, 4, 0.7), (1, 14, 2, 0.5),
]
KEYS_B = [
    (0, 0, 2, 0.75), (0, 3, 1, 0.5), (0, 6, 2, 0.6), (0, 10, 2, 0.65), (0, 13, 2, 0.55),
    (1, 2, 3, 0.65), (1, 7, 1.5, 0.5), (1, 10, 4, 0.7),
]

# (bar in chord, step, index into the vocal notes, length in steps, vowels, fall in semitones)
VOX_CALL = [
    (1, 0, 3, 1.5, "oa", 0), (1, 3, 2, 1.0, "aa", 0), (1, 6, 3, 2.5, "oa", 0),
    (1, 10, 4, 1.0, "ao", 0), (1, 12, 3, 3.5, "ou", 2),
]
VOX_ANSWER = [(0, 6, 4, 1.0, "aa", 0), (0, 10, 3, 2.0, "oa", 1)]
CALL_CHORDS = {0, 2, 4, 5, 6, 7}  # chord slots 0-7 across the 16 bars
ANSWER_CHORDS = {5, 7}

# Closed hat velocity per 16th. The gaps are where the open hats go.
HATS = [0.5, 0.3, 0, 0.42, 0.45, 0.28, 0, 0.4, 0.5, 0.3, 0, 0.42, 0.45, 0.28, 0, 0.45]


def build():
    song = Song(bpm=TRACK["bpm"], bars=TRACK["bars"], swing=0.62, seed=11)
    rng = song.rng
    step = song.step_s

    def seed():
        return int(rng.integers(1_000_000))

    kits = {
        "kick": [inst.kick()],
        "snare": [inst.garage_snare(seed=s) for s in range(3)],
        "hat": [inst.hat(seed=s) for s in range(4)],
        "open": [inst.hat(open_=True, seed=s) for s in range(3)],
        "rim": [inst.rim(seed=s) for s in range(3)],
        "shaker": [inst.shaker(seed=s) for s in range(4)],
    }

    def hit(bus, kit, bar, st, vel, gain, pan_to=0.0, jitter=0.0):
        t = song.at(bar, st, jitter_ms=jitter)
        sounds = kits[kit]
        song.add(bus, sounds[rng.integers(len(sounds))], t, gain * vel * rng.uniform(0.93, 1.0), pan_to)
        return t

    # Drums
    kick_hits = []
    for bar in range(song.bars):
        odd = bar % 2 == 1
        for st, vel in [(0, 1.0), (10, 0.9)] + ([(7, 0.55)] if odd else []):
            t = hit("kick", "kick", bar, st, vel, 0.9)
            if vel > 0.8:
                kick_hits.append(dsp.samples(t))

        snares = {4: 1.0, 12: 1.0}
        if odd:
            snares[15] = 0.22
        if bar % 4 == 3:
            snares[9] = 0.18
        if bar in (7, 15):
            snares.update({13: 0.25, 14: 0.35, 15: 0.5})
        for st, vel in snares.items():
            hit("snare", "snare", bar, st, vel, 0.55, jitter=1.5)

        for st, vel in ((3, 0.3), (14, 0.28)) if odd else ((7, 0.32), (13, 0.26)):
            hit("perc", "rim", bar, st, vel, 0.25, pan_to=-0.3, jitter=3)
        for st, vel in enumerate(HATS):
            if vel:
                hit("hats", "hat", bar, st, vel, 0.17, pan_to=0.2, jitter=3)
        for st in (2, 6, 10, 14):
            hit("hats", "open", bar, st, 0.42, 0.14, pan_to=-0.15, jitter=2)
        if bar >= 8:
            for st in range(16):
                hit("perc", "shaker", bar, st, 0.25 if st % 2 == 0 else 0.16, 0.12, pan_to=0.35, jitter=4)

    song.add("fx", inst.crash(seed=1), song.at(0), 0.12, pan_to=0.25)
    song.add("fx", inst.crash(seed=2), song.at(8), 0.10, pan_to=-0.25)
    for end_bar, beats, gain in ((8, 2, 0.06), (16, 4, 0.1)):
        rise = inst.swell(beats * 4 * step, seed=end_bar)
        song.add("fx", rise, song.at(end_bar) - len(rise) / dsp.SR, gain)

    # Bass, keys, pad and vocal, one chord (two bars) at a time
    prev = dsp.note(CHORDS[0][0]) - 1  # the last bass note of the loop, leading into F
    for slot in range(song.bars // 2):
        root, third, seventh, voicing, vox_notes = CHORDS[slot % len(CHORDS)]
        r = dsp.note(root)
        roles = {"3rd": third, "7th": seventh - 12,
                 "approach": dsp.note(CHORDS[(slot + 1) % len(CHORDS)][0]) - 1 - r}
        first_bar = slot * 2

        for b, st, interval, length, glide in BASS:
            m = r + (roles[interval] if isinstance(interval, str) else interval)
            sound = inst.bass(m, length * step * 0.92, glide_from=prev if glide else None)
            song.add("bass", sound, song.at(first_bar + b, st), 0.42)
            prev = m

        for b, st, length, vel in KEYS_A if slot < 4 else KEYS_B:
            stab = inst.strum(inst.epiano, voicing, length * step, vel, seed=seed())
            song.add("keys", stab, song.at(first_bar + b, st, jitter_ms=4), 0.17)

        song.add("pad", inst.pad(voicing, 2 * 16 * step - 0.3, seed=seed()), song.at(first_bar), 0.17)

        phrases = (VOX_CALL if slot in CALL_CHORDS else []) + (VOX_ANSWER if slot in ANSWER_CHORDS else [])
        for b, st, idx, length, vowels, fall in phrases:
            sound = inst.vox(vox_notes[idx], length * step, vowels=vowels, fall=fall, seed=seed())
            song.add("vox", sound, song.at(first_bar + b, st, jitter_ms=3), 0.28,
                     pan_to=rng.uniform(-0.15, 0.15))

    # Mix
    n = song.length
    bus = {name: song.bus(name) for name in ("kick", "snare", "hats", "perc", "bass", "keys", "pad", "vox", "fx")}

    drums = bus["kick"] + bus["snare"] + bus["hats"] + bus["perc"]
    drums = dsp.on_loop(dsp.saturate(drums, 1.4), lambda s: dsp.lowpass(s, 9500))
    bass = dsp.on_loop(bus["bass"], lambda s: dsp.lowpass(s, 1600)) * dsp.duck(n, kick_hits, 0.45, 0.09)
    keys = dsp.on_loop(bus["keys"], lambda s: dsp.lowpass(dsp.highpass(s, 140), 4200))
    keys = dsp.tape_wobble(keys) * dsp.duck(n, kick_hits, 0.3, 0.16)
    pad = dsp.tape_wobble(bus["pad"]) * dsp.duck(n, kick_hits, 0.55, 0.22)
    vox = dsp.on_loop(bus["vox"], lambda s: dsp.lowpass(dsp.highpass(s, 280), 6500))
    vox = dsp.tape_wobble(dsp.crush(vox, bits=12, hold=2))
    delay = dsp.loop_convolve(vox, dsp.delay_ir(3 * step, feedback=0.42)) * 0.22
    sends = (keys * 0.25 + pad * 0.4 + vox * 0.45 + bus["snare"] * 0.12 + bus["perc"] * 0.15
             + bus["fx"] * 0.6 + delay * 0.3)
    verb = dsp.loop_convolve(sends, dsp.reverb_ir(2.4)) * 0.35
    vinyl = inst.vinyl(n, seed=3)

    parts = {"drums": drums, "bass": bass, "keys": keys, "pad": pad, "vox": vox,
             "fx": bus["fx"], "delay": delay, "reverb": verb, "vinyl": vinyl}
    return dsp.master(sum(parts.values())), parts
