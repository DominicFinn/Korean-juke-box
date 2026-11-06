"""Sunny Shore: lo-fi reggae in G major, 75 BPM, 16 bars.

A one-drop beat (kick and cross-stick together on three), guitar skanks on two and
four with an organ bubbling on the off-beats, and a deep round bass carrying the
tune. The second half brings in a melodica, and dub echoes throw the odd skank and
snare off into the distance. Waves wash in underneath, for beach levels.
"""
from lofi import Song, dsp, inst

TRACK = {"title": "Sunny Shore", "title_ko": "맑은 해변", "style": "Lo-fi reggae",
         "bpm": 75, "bars": 16, "key": "G major"}

# One bar per chord: (skank voicing, organ voicing, bass line as (step, note, length))
CHORDS = [
    (("G3", "B3", "D4", "G4"), ("B3", "D4", "G4"),        # G
     [(0, "G1", 3), (4, "G1", 1), (6, "B1", 2), (8, "D2", 3.5), (12, "B1", 2), (14, "A1", 2)]),
    (("G3", "C4", "E4", "G4"), ("C4", "E4", "G4"),        # C
     [(0, "C2", 3), (4, "C2", 1), (6, "E2", 2), (8, "G1", 3.5), (12, "A1", 2), (14, "B1", 2)]),
    (("A3", "C4", "E4", "G4"), ("C4", "E4", "G4"),        # Am7
     [(0, "A1", 3), (4, "A1", 1), (6, "C2", 2), (8, "E2", 3.5), (12, "D2", 2), (14, "C2", 2)]),
    (("A3", "D4", "F#4", "A4"), ("C4", "D4", "F#4"),      # D7
     [(0, "D2", 3), (4, "D2", 1), (6, "F#1", 2), (8, "A1", 3.5), (12, "C2", 2), (14, "F#1", 2)]),
]

# Melodica tune for bars 8 to 15: (bar, step, note, length in steps)
MELODICA = [
    (0, 2, "B4", 2), (0, 4, "D5", 4), (0, 10, "B4", 2), (0, 12, "A4", 4),
    (1, 2, "G4", 2), (1, 4, "E5", 6), (1, 12, "D5", 4),
    (2, 2, "C5", 2), (2, 4, "E5", 4), (2, 10, "D5", 2), (2, 12, "C5", 4),
    (3, 0, "A4", 6), (3, 8, "F#4", 2), (3, 10, "A4", 2), (3, 12, "D5", 4),
    (4, 2, "G5", 2), (4, 4, "D5", 4), (4, 10, "E5", 2), (4, 12, "D5", 4),
    (5, 2, "C5", 2), (5, 4, "E5", 2), (5, 6, "G5", 4), (5, 12, "E5", 4),
    (6, 2, "C5", 2), (6, 4, "A4", 4), (6, 10, "B4", 2), (6, 12, "C5", 4),
    (7, 0, "D5", 8), (7, 10, "C5", 2), (7, 12, "A4", 4),
]


def build():
    song = Song(bpm=TRACK["bpm"], bars=TRACK["bars"], swing=0.57, seed=41)
    rng = song.rng
    step = song.step_s

    def seed():
        return int(rng.integers(1_000_000))

    kits = {
        "kick": [inst.kick(seed=s, decay=0.3) for s in range(2)],
        "rim": [inst.rim(seed=s) for s in range(3)],
        "snare": [inst.dusty_snare(seed=s) for s in range(2)],
        "hat": [inst.hat(seed=s) for s in range(4)],
        "open": [inst.hat(open_=True, seed=s) for s in range(2)],
    }

    def hit(bus, kit, bar, st, vel, gain, pan_to=0.0, jitter=0.0):
        t = song.at(bar, st, jitter_ms=jitter)
        sounds = kits[kit]
        song.add(bus, sounds[rng.integers(len(sounds))], t, gain * vel * rng.uniform(0.92, 1.0), pan_to)
        return t

    kick_hits = []
    for bar in range(song.bars):
        # The one drop: nothing on one, kick and cross-stick together on three
        kick_hits.append(dsp.samples(hit("kick", "kick", bar, 8, 1.0, 0.6)))
        # Every fourth bar the cross-stick is thrown into the dub echo instead
        hit("dub" if bar % 4 == 3 else "rim", "rim", bar, 8, 0.9, 0.35, pan_to=-0.1, jitter=2)
        for st in range(0, 16, 2):
            hit("hats", "hat", bar, st, 0.45 if st % 4 == 2 else 0.25, 0.14, pan_to=0.3, jitter=4)
        if bar % 2 == 1:
            hit("hats", "hat", bar, 15, 0.3, 0.12, pan_to=0.3, jitter=3)
            hit("hats", "open", bar, 6, 0.35, 0.1, pan_to=-0.25, jitter=3)
        if bar == song.bars - 1:
            for st, vel in ((12, 0.4), (13, 0.5), (14, 0.65), (15, 0.8)):
                hit("dub", "snare", bar, st, vel, 0.45, jitter=3)

    for bar in range(song.bars):
        skank, organ_notes, bass_line = CHORDS[bar % len(CHORDS)]
        for st in (4, 12):
            chop = inst.strum_guitar(skank, 0.09, down=False, vel=0.9, seed=seed(), spread=0.004, brightness=0.8)
            # Some skanks get sent off into the echo
            bus = "dub" if (bar % 4 == 1 and st == 12) else "skank"
            song.add(bus, chop, song.at(bar, st, jitter_ms=3), 0.85, pan_to=0.35)
        for st in (2, 6, 10, 14):
            bubble = inst.strum(inst.organ, organ_notes, 0.07, 0.6, spread=0.0, seed=seed())
            song.add("organ", bubble, song.at(bar, st, jitter_ms=2), 0.4, pan_to=-0.35)
        for st, name, length in bass_line:
            song.add("bass", inst.bass(name, length * step * 0.9), song.at(bar, st), 0.6)

    for b, st, name, length in MELODICA:
        song.add("lead", inst.melodica(name, length * step * 0.95, vel=0.8, seed=seed()),
                 song.at(8 + b, st, jitter_ms=5), 0.2, pan_to=0.15)

    n = song.length
    bus = {name: song.bus(name) for name in ("kick", "rim", "hats", "skank", "organ", "bass", "lead", "dub")}
    drums = dsp.on_loop(dsp.saturate(bus["kick"] + bus["rim"] + bus["hats"], 1.4), lambda s: dsp.lowpass(s, 8000))
    bass = dsp.on_loop(bus["bass"], lambda s: dsp.lowpass(s, 700)) * dsp.duck(n, kick_hits, 0.25, 0.12)
    skank = dsp.on_loop(bus["skank"] + bus["dub"] * 0.6, lambda s: dsp.lowpass(dsp.highpass(s, 350), 6000))
    organ = dsp.tape_wobble(dsp.on_loop(bus["organ"], lambda s: dsp.lowpass(dsp.highpass(s, 200), 3500)))
    lead = dsp.tape_wobble(dsp.on_loop(bus["lead"], lambda s: dsp.highpass(s, 250)), wow_ms=1.0)
    # Dub echo: long dotted-eighth repeats that get darker as they fade
    dub = dsp.loop_convolve(dsp.highpass(bus["dub"], 300), dsp.delay_ir(3 * step, feedback=0.62, repeats=9, damping=2200))
    lead_echo = dsp.loop_convolve(lead, dsp.delay_ir(3 * step, feedback=0.3, damping=2500)) * 0.25
    sends = skank * 0.2 + organ * 0.2 + lead * 0.35 + dub * 0.3 + bus["rim"] * 0.2
    verb = dsp.loop_convolve(sends, dsp.reverb_ir(2.0, brightness=5000)) * 0.3
    beach = inst.waves(n, seed=12, amount=1.0) + inst.vinyl(n, seed=13, amount=0.8)

    parts = {"drums": drums, "bass": bass, "skank": skank, "organ": organ, "lead": lead,
             "dub": dub * 1.3, "echo": lead_echo, "reverb": verb, "beach": beach}
    return dsp.master(sum(parts.values())), parts
