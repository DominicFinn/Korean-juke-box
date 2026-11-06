"""Rooftop Arcade: lo-fi house in A minor, 122 BPM, 16 bars.

Four-on-the-floor with off-beat open hats and an off-beat bass, and dusty organ
stabs behind a filter that opens across the first eight bars and closes again
before the loop comes round. The second half adds a ride and quiet arcade bleeps.
For exploring, shopping and city maps.
"""
import numpy as np

from lofi import Song, dsp, inst

TRACK = {"title": "Rooftop Arcade", "title_ko": "옥상 오락실", "style": "Lo-fi house",
         "bpm": 122, "bars": 16, "key": "A minor"}

# Two bars per chord: (bass root, organ voicing, bleep notes)
CHORDS = [
    ("A1", ("G3", "B3", "C4", "E4"), ("A5", "C6", "E6")),   # Am9
    ("F1", ("G3", "A3", "C4", "E4"), ("F5", "A5", "C6")),   # Fmaj9
    ("D2", ("F3", "A3", "C4", "E4"), ("D5", "F5", "A5")),   # Dm9
    ("E2", ("G3", "B3", "D4", "E4"), ("E5", "G5", "B5")),   # Em7
]

# Organ stabs over two bars: (bar in chord, step, length in steps, velocity)
STABS = [
    (0, 0, 1.5, 0.8), (0, 3, 1.5, 0.6), (0, 6, 2, 0.7), (0, 10, 1.5, 0.6), (0, 13, 2, 0.7),
    (1, 2, 1.5, 0.6), (1, 6, 2, 0.75), (1, 9, 1.5, 0.6), (1, 12, 3, 0.7),
]

# Off-beat bass: (step, interval above the root, length in steps)
BASS = [(2, 0, 1.5), (6, 0, 1.5), (10, 12, 1.5), (14, 7, 1.5)]


def build():
    song = Song(bpm=TRACK["bpm"], bars=TRACK["bars"], swing=0.56, seed=91)
    rng = song.rng
    step = song.step_s

    def seed():
        return int(rng.integers(1_000_000))

    kits = {
        "kick": [inst.kick(seed=s, decay=0.16) for s in range(2)],
        "clap": [inst.clap(seed=s) for s in range(3)],
        "hat": [inst.hat(seed=s) for s in range(4)],
        "open": [inst.hat(open_=True, seed=s) for s in range(3)],
        "ride": [inst.ride(seed=s) for s in range(2)],
        "shaker": [inst.shaker(seed=s) for s in range(4)],
    }

    def hit(bus, kit, bar, st, vel, gain, pan_to=0.0, jitter=0.0):
        t = song.at(bar, st, jitter_ms=jitter)
        sounds = kits[kit]
        song.add(bus, sounds[rng.integers(len(sounds))], t, gain * vel * rng.uniform(0.92, 1.0), pan_to)
        return t

    kick_hits = []
    for bar in range(song.bars):
        last = bar == song.bars - 1
        for st in (0, 4, 8, 12):
            # The kick drops out for the last beat of the loop
            if last and st == 12:
                continue
            kick_hits.append(dsp.samples(hit("drums", "kick", bar, st, 1.0, 0.75, jitter=1)))
        for st in (4, 12):
            hit("drums", "clap", bar, st, 0.85, 0.4, jitter=2)
        for st in (2, 6, 10, 14):
            hit("drums", "open", bar, st, 0.5, 0.18, pan_to=-0.2, jitter=2)
        for st in range(16):
            if st % 4 != 2:
                hit("drums", "hat", bar, st, 0.35 if st % 2 else 0.2, 0.16, pan_to=0.3, jitter=3)
        hit("drums", "shaker", bar, 15, 0.4, 0.12, pan_to=0.4, jitter=3)
        if bar >= 8:
            for st in (0, 4, 8, 12):
                hit("drums", "ride", bar, st + 2, 0.4, 0.09, pan_to=-0.4, jitter=2)

    for slot in range(song.bars // 2):
        root, voicing, bleeps = CHORDS[slot % len(CHORDS)]
        r = dsp.note(root)
        for b, st, length, vel in STABS:
            stab = inst.strum(inst.organ, voicing, length * step, vel, spread=0.002, seed=seed())
            song.add("organ", stab, song.at(slot * 2 + b, st, jitter_ms=2), 0.5, pan_to=-0.1)
        for b in (0, 1):
            for st, interval, length in BASS:
                song.add("bass", inst.bass(r + 12 + interval, length * step * 0.9), song.at(slot * 2 + b, st), 0.5)
        song.add("pad", inst.pad(voicing, 32 * step - 0.3, cutoff=1200, seed=seed()), song.at(slot * 2), 0.2)
        if slot >= 4:
            for b, st in ((0, 7), (1, 11)):
                bleep = inst.chip_arp(bleeps, step * 2, 0.045, vel=0.5)
                song.add("bleeps", bleep, song.at(slot * 2 + b, st), 0.24, pan_to=0.45)

    rise = inst.swell(4 * step, seed=10)
    song.add("fx", rise, song.at(16) - len(rise) / dsp.SR, 0.08)
    song.add("fx", inst.crash(seed=11), song.at(8), 0.1, pan_to=0.3)

    n = song.length
    bus = {name: song.bus(name) for name in ("drums", "organ", "bass", "pad", "bleeps", "fx")}
    drums = dsp.on_loop(dsp.saturate(bus["drums"], 1.4), lambda s: dsp.lowpass(s, 9500))
    bass = dsp.on_loop(bus["bass"], lambda s: dsp.lowpass(s, 800)) * dsp.duck(n, kick_hits, 0.4, 0.08)

    # The organ filter opens over the first eight bars, stays open, then closes in the
    # last two bars so the loop starts dusty again
    bars = np.arange(n) / n * song.bars
    sweep = np.interp(bars, [0, 8, 14, 16], [0.0, 1.0, 1.0, 0.0])
    organ = dsp.moving_lowpass(bus["organ"], sweep, 500, 6000)
    organ = dsp.tape_wobble(dsp.on_loop(organ, lambda s: dsp.highpass(s, 180))) * dsp.duck(n, kick_hits, 0.35, 0.12)
    pad = dsp.tape_wobble(dsp.on_loop(bus["pad"], lambda s: dsp.highpass(s, 250))) * dsp.duck(n, kick_hits, 0.5, 0.15)
    bleeps = dsp.on_loop(dsp.crush(bus["bleeps"], bits=8), lambda s: dsp.highpass(s, 500))
    echo = dsp.loop_convolve(organ * 0.5 + bleeps, dsp.delay_ir(3 * step, feedback=0.35, damping=2500)) * 0.2
    sends = organ * 0.25 + pad * 0.3 + bleeps * 0.3 + bus["fx"] * 0.5
    verb = dsp.loop_convolve(sends, dsp.reverb_ir(1.8, brightness=5000)) * 0.3

    parts = {"drums": drums, "bass": bass, "organ": organ, "pad": pad, "bleeps": bleeps, "fx": bus["fx"],
             "echo": echo, "reverb": verb, "vinyl": inst.vinyl(n, seed=18, amount=0.8)}
    return dsp.master(sum(parts.values())), parts
