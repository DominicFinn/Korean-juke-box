"""Best: lo-fi hip hop on the tune Dom recorded (inbox/Best.m4a), 12 bars.

The tune was transcribed from the recording with lofi/recording.py: ten phrases in A
major, one a bar at the singer's own pace of about 72 BPM, with each syllable a 16th
note. No voice is used; the MELODY table below is the tune, so it can be edited by hand.

The harmony builds through the loop. A marimba plays the tune note for note, alone for
two bars, then with a second marimba a third above. A flute takes over with the repeated
notes joined up, and a second flute joins it a sixth below. In the last two bars the
marimba and flute play the opening and closing phrases together in thirds, then it all
comes round again. Harmony notes stay in A major, so they always fit the chords.
"""
from lofi import Song, dsp, inst

TRACK = {"title": "Best", "title_ko": "최고야", "style": "Lo-fi hip hop on Dom's tune",
         "bpm": 72, "bars": 12, "key": "A major"}

# One phrase a bar, as sung (an octave below where it's played): (step, length in steps, note)
MELODY = [
    [(0, 1, "A3"), (1, 1, "A3"), (2, 1, "A3"), (3, 1, "A3"), (4, 1, "A3"), (5, 1, "A3"), (6, 1, "A3"),
     (7, 1, "B3"), (8, 1, "B3"), (9, 1, "B3"), (10, 1, "B3"), (11, 1, "A3"), (12, 1, "A3"), (13, 1, "G#3")],
    [(0, 1, "A3"), (1, 1, "A3"), (2, 1, "A3"), (3, 1, "A3"), (4, 1, "A3"), (5, 1, "A3"), (6, 1, "A3"),
     (7, 1, "B3"), (8, 1, "B3"), (9, 1, "B3"), (10, 1, "B3"), (11, 1, "A3"), (12, 1, "G#3"), (13, 1, "G#3")],
    [(1, 1, "B3"), (2, 1, "C#4"), (3, 1, "A3"), (5, 1, "C#4"), (8, 1, "C#4"), (9, 1, "B3"), (10, 1, "C#4"),
     (11, 1, "A3"), (12, 2, "A3"), (14, 1, "A3")],
    [(1, 1, "A3"), (2, 1, "A3"), (3, 1, "A3"), (6, 1, "A3"), (7, 1, "B3"), (8, 1, "C#4"), (9, 1, "B3"),
     (10, 1, "C#4"), (11, 1, "A3"), (12, 1, "A3"), (13, 1, "G#3"), (14, 1, "G#3")],
    [(1, 1, "C#4"), (2, 1, "A3"), (5, 1, "C#4"), (6, 1, "A3"), (8, 1, "C#4"), (10, 1, "C#4"), (11, 1, "B3"),
     (12, 1, "A3"), (13, 1, "A3"), (14, 1, "G#3")],
    [(0, 1, "C#4"), (1, 1, "C#4"), (2, 1, "C#4"), (4, 1, "C#4"), (5, 1, "C#4"), (6, 1, "A3"), (8, 2, "C#4"),
     (10, 1, "B3"), (13, 1, "A3")],
    [(0, 1, "A3"), (2, 1, "E4"), (3, 1, "A3"), (4, 1, "A3"), (5, 1, "A3"), (6, 1, "A3"), (7, 1, "G#3"),
     (8, 1, "A3"), (10, 1, "A3"), (11, 1, "A3"), (12, 1, "C#4"), (14, 1, "C#4")],
    [(0, 1, "G#3"), (1, 1, "E4"), (2, 1, "A3"), (3, 1, "A3"), (4, 1, "A3"), (5, 1, "A3"), (6, 1, "A3"),
     (7, 1, "G#3"), (8, 1, "G#3"), (10, 1, "A3"), (11, 1, "A3"), (12, 1, "A3"), (13, 1, "C#4"), (14, 1, "C#4")],
    [(0, 1, "D4"), (1, 1, "C#4"), (2, 1, "C#4"), (3, 1, "C#4"), (4, 1, "C#4"), (5, 1, "C#4"), (6, 1, "A3"),
     (7, 2, "B3"), (9, 1, "C#4"), (10, 1, "C#4"), (12, 1, "A3")],
    [(1, 1, "C#4"), (3, 1, "A3"), (5, 1, "C#4"), (6, 1, "A3"), (8, 1, "C#4"), (9, 1, "B3"), (10, 1, "C#4"),
     (11, 1, "B3"), (12, 1, "A3"), (13, 1, "F#3"), (14, 1, "G#3"), (15, 1, "A3")],
]

# Which bars get what. The marimba has the tune first and the flute after it.
MARIMBA_BARS = range(0, 5)
MARIMBA_HARMONY_BARS = range(2, 5)
FLUTE_HARMONY_BARS = range(7, 10)
# The last two bars replay these phrases with both instruments in thirds
REPRISE = {10: 0, 11: 9}

# A major, as pitch classes, for moving the tune up and down the scale
SCALE = (9, 11, 1, 2, 4, 6, 8)
SCALE_NOTES = [m for m in range(24, 108) if m % 12 in SCALE]

# One chord a bar, four-bar cycle, voiced below the tune. Every note in it (A, B, C#, D,
# E, F#, G#) sits inside these: (bass root, fifth, Rhodes voicing)
CHORDS = [
    ("A1", "E2", ("E3", "G#3", "B3", "C#4")),   # Amaj9
    ("F#1", "C#2", ("E3", "G#3", "A3", "C#4")),  # F#m9
    ("D2", "A2", ("E3", "F#3", "A3", "C#4")),   # Dmaj9
    ("E2", "B2", ("D3", "F#3", "A3", "B3")),    # E9sus4
]

# (step, length in steps, velocity): long, lazy chords with a push into the next bar
KEYS = [(0, 7, 0.6), (10, 3, 0.4), (14, 2, 0.35)]

# (step, role, length in steps)
BASS = [(0, "root", 6), (7, "fifth", 2), (10, "root", 3), (14, "approach", 2)]

HATS = [0.5, 0.18, 0.32, 0.16, 0.45, 0.18, 0.32, 0.2, 0.5, 0.18, 0.32, 0.16, 0.45, 0.2, 0.3, 0.22]


def in_scale(midi, steps):
    """Move a note up or down the A major scale: 2 steps is a third, -5 a sixth below."""
    return SCALE_NOTES[SCALE_NOTES.index(midi) + steps]


def joined(phrase):
    """The same phrase with repeated notes run together, for an instrument that holds
    notes rather than tapping them out."""
    result = []
    for step, length, name in phrase:
        if result and result[-1][2] == name and step <= result[-1][0] + result[-1][1] + 1:
            first = result[-1][0]
            result[-1] = (first, step + length - first, name)
        else:
            result.append((step, length, name))
    return result


def build():
    song = Song(bpm=TRACK["bpm"], bars=TRACK["bars"], swing=0.56, seed=31)
    rng = song.rng
    step = song.step_s

    def seed():
        return int(rng.integers(1_000_000))

    kits = {
        "kick": [inst.kick(seed=s, decay=0.28) for s in range(2)],
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

    # Drums: the first bar is just keys and marimba, so the loop opens gently
    kick_hits = []
    for bar in range(1, song.bars):
        kicks = [(0, 1.0), (10, 0.8)] + ([(7, 0.45)] if bar % 2 else [(13, 0.4)])
        for st, vel in kicks:
            t = hit("kick", "kick", bar, st, vel, 0.85, jitter=2)
            if vel > 0.7:
                kick_hits.append(dsp.samples(t))
        for st, vel in [(4, 1.0), (12, 1.0)] + ([(15, 0.22)] if bar % 4 == 3 else []):
            hit("snare", "snare", bar, st, vel, 0.55, jitter=4)
        for st, vel in enumerate(HATS):
            hit("hats", "hat", bar, st, vel, 0.14, pan_to=0.25, jitter=5)
        if bar % 2 == 1:
            hit("hats", "open", bar, 14, 0.45, 0.1, pan_to=-0.2, jitter=3)
        if bar >= 10:
            hit("perc", "rim", bar, 7, 0.35, 0.22, pan_to=-0.35, jitter=4)

    # Chords and bass, one chord a bar
    for bar in range(song.bars):
        root, fifth, voicing = CHORDS[bar % len(CHORDS)]
        r = dsp.note(root)
        next_root = dsp.note(CHORDS[(bar + 1) % len(CHORDS)][0])
        roles = {"root": r, "fifth": dsp.note(fifth), "approach": next_root - 1 if next_root > r else next_root + 1}
        for st, length, vel in KEYS:
            stab = inst.strum(inst.epiano, voicing, length * step, vel, spread=0.016, seed=seed())
            song.add("keys", stab, song.at(bar, st, jitter_ms=8), 0.24)
        if bar >= 1:
            for st, role, length in BASS:
                song.add("bass", inst.upright(roles[role], length * step * 0.9, vel=0.9),
                         song.at(bar, st, jitter_ms=4), 0.6)
        song.add("pad", inst.pad(voicing, 16 * step, cutoff=900, seed=seed()), song.at(bar), 0.1)

    def marimba(bar, phrase, steps=0, gain=0.55, pan_to=0.1):
        for st, length, name in phrase:
            accent = 0.75 if st % 4 == 0 else 0.6 if st % 2 == 0 else 0.5
            midi = in_scale(dsp.note(name) + 12, steps)
            song.add("lead", inst.marimba(midi, max(length, 2) * step, vel=accent),
                     song.at(bar, st, jitter_ms=5), gain, pan_to=pan_to)

    def flute(bar, phrase, steps=0, gain=0.5, pan_to=-0.05):
        for st, length, name in joined(phrase):
            midi = in_scale(dsp.note(name) + 12, steps)
            song.add("lead", inst.flute(midi, length * step * 0.95, vel=0.65, seed=seed()),
                     song.at(bar, st, jitter_ms=5), gain, pan_to=pan_to)

    # The tune, an octave up from where it was sung, with its harmonies
    for bar, phrase in enumerate(MELODY):
        if bar in MARIMBA_BARS:
            marimba(bar, phrase)
            if bar in MARIMBA_HARMONY_BARS:
                marimba(bar, phrase, steps=2, gain=0.33, pan_to=-0.3)
        else:
            flute(bar, phrase)
            if bar in FLUTE_HARMONY_BARS:
                flute(bar, phrase, steps=-5, gain=0.32, pan_to=0.3)
    for bar, source in REPRISE.items():
        marimba(bar, MELODY[source], gain=0.45, pan_to=0.25)
        flute(bar, MELODY[source], steps=2, gain=0.36, pan_to=-0.25)

    rise = inst.swell(4 * step, seed=6)
    song.add("fx", rise, song.at(song.bars) - len(rise) / dsp.SR, 0.05)

    n = song.length
    bus = {name: song.bus(name) for name in ("kick", "snare", "hats", "perc", "bass", "keys", "pad",
                                             "lead", "fx")}
    drums = bus["kick"] + bus["snare"] + bus["hats"] + bus["perc"]
    drums = dsp.on_loop(dsp.saturate(drums, 1.5), lambda s: dsp.lowpass(s, 7500))
    bass = dsp.on_loop(bus["bass"], lambda s: dsp.lowpass(s, 900)) * dsp.duck(n, kick_hits, 0.3, 0.1)
    keys = dsp.on_loop(bus["keys"], lambda s: dsp.lowpass(dsp.highpass(s, 140), 3400))
    keys = dsp.tape_wobble(keys, wow_ms=1.2) * dsp.duck(n, kick_hits, 0.2, 0.15)
    pad = dsp.tape_wobble(bus["pad"], wow_ms=1.2)
    lead = dsp.on_loop(bus["lead"], lambda s: dsp.lowpass(dsp.highpass(s, 200), 6000))
    lead = dsp.tape_wobble(dsp.saturate(lead, 1.2), wow_ms=0.9)
    echo = dsp.loop_convolve(lead * 0.6, dsp.delay_ir(3 * step, feedback=0.3, damping=2500)) * 0.18
    sends = lead * 0.3 + keys * 0.3 + pad * 0.4 + bus["snare"] * 0.1 + bus["fx"] * 0.5 + echo * 0.3
    verb = dsp.loop_convolve(sends, dsp.reverb_ir(2.2, brightness=4500)) * 0.33
    weather = inst.rain(n, seed=12, amount=0.8) + inst.vinyl(n, seed=13, amount=1.2)

    parts = {"lead": lead, "drums": drums, "bass": bass, "keys": keys, "pad": pad,
             "fx": bus["fx"], "echo": echo, "reverb": verb, "rain": weather}
    return dsp.master(sum(parts.values())), parts
