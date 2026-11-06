"""Instruments and drum voices, all synthesised. Each returns a mono (n,) or stereo
(n, 2) array starting at its onset, ready to drop into a Song bus."""
import numpy as np

from .dsp import (SR, bandpass, crush, envelope, fade_in, fade_out, highpass, hz, lowpass,
                  normalise, note, on_loop, pan, phase, pulse, samples, saw, time_axis)


# Drums

def kick(seed=0, decay=0.2):
    """Round, slightly saturated kick: a sine diving from ~190 Hz to 46 Hz."""
    rng = np.random.default_rng(seed)
    n = samples(0.5)
    t = time_axis(n)
    freq = 46 + 115 * np.exp(-t / 0.032) + 30 * np.exp(-t / 0.004)
    body = np.sin(phase(freq)) * np.exp(-t / decay)
    click = lowpass(rng.standard_normal(n), 3500) * np.exp(-t / 0.003) * 0.25
    x = lowpass(np.tanh(2.0 * (body + click)), 5000)
    return normalise(fade_out(fade_in(x, 0.0005), 0.04))


def _snare(rng, n, t):
    tone = (np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05) * 0.5
            + np.sin(2 * np.pi * 340 * t) * np.exp(-t / 0.03) * 0.25)
    noise = bandpass(rng.standard_normal(n), 1200, 7000) * np.exp(-t / 0.11) * 0.55
    return np.tanh(1.5 * (tone + noise))


def _clap(rng, n, t):
    noise = bandpass(rng.standard_normal(n), 900, 4000, order=2)
    env = np.zeros(n)
    for offset in (0.0, 0.009, 0.018, 0.026):
        s = samples(offset)
        env[s:] += np.exp(-(t[s:] - offset) / 0.006)
    s = samples(0.026)
    env[s:] += 0.6 * np.exp(-(t[s:] - 0.026) / 0.11)
    return noise * env


def garage_snare(seed=0):
    """Snare and clap layered, then crunched like an old sampler."""
    rng = np.random.default_rng(seed)
    n = samples(0.4)
    t = time_axis(n)
    x = 0.55 * normalise(_snare(rng, n, t)) + 0.75 * normalise(_clap(rng, n, t))
    return normalise(fade_out(crush(x, bits=12, hold=2), 0.03))


_METAL = (205.3, 304.4, 369.6, 522.7, 540.0, 800.0)  # the 808's six hat oscillators


def hat(open_=False, seed=0):
    rng = np.random.default_rng(seed)
    n = samples(0.35 if open_ else 0.09)
    t = time_axis(n)
    metal = sum(np.sign(np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi))) for f in _METAL) / 6
    x = highpass(0.6 * metal + 0.5 * rng.standard_normal(n), 7000)
    x = lowpass(x, 11000) * np.exp(-t / (0.09 if open_ else 0.016))
    return normalise(fade_out(fade_in(x, 0.0005), 0.01))


def shaker(seed=0):
    rng = np.random.default_rng(seed)
    n = samples(0.12)
    t = time_axis(n)
    x = bandpass(rng.standard_normal(n), 3500, 9000, order=2)
    x *= (1 - np.exp(-t / 0.012)) * np.exp(-t / 0.035)
    return normalise(fade_out(x, 0.01))


def rim(seed=0):
    rng = np.random.default_rng(seed)
    n = samples(0.12)
    t = time_axis(n)
    x = (np.sin(2 * np.pi * 1650 * t) * np.exp(-t / 0.010)
         + 0.6 * np.sin(2 * np.pi * 820 * t) * np.exp(-t / 0.022)
         + 0.5 * highpass(rng.standard_normal(n), 2000) * np.exp(-t / 0.002))
    return normalise(fade_out(bandpass(x, 500, 6000), 0.01))


def crash(seconds=2.4, seed=0):
    rng = np.random.default_rng(seed)
    n = samples(seconds)
    t = time_axis(n)
    freqs = rng.uniform(3000, 9500, 40)
    metal = np.zeros(n)
    for f in freqs:
        metal += np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi))
    x = 0.5 * metal / np.sqrt(len(freqs)) + 0.7 * rng.standard_normal(n)
    x = lowpass(highpass(x, 3500), 10000) * np.exp(-t / 0.7)
    return normalise(fade_out(fade_in(x, 0.002), 0.2))


def swell(seconds, seed=0):
    """Reverse-cymbal style noise rise that stops dead on the next downbeat."""
    rng = np.random.default_rng(seed)
    n = samples(seconds)
    t = time_axis(n)
    x = bandpass(rng.standard_normal((n, 2)), 1500, 9000) * ((t / seconds) ** 3)[:, None]
    return normalise(fade_out(x, 0.004))


# Tonal

def epiano(midi, gate, vel=0.8, seed=0):
    """FM electric piano, a rough Rhodes: a 1:1 FM body, a short 14:1 'tine' on the
    attack and a slow tremolo across the stereo field."""
    rng = np.random.default_rng(seed)
    f = hz(midi) * (1 + rng.normal(0, 0.0006))
    release = 0.45
    n = samples(gate + release)
    t = time_axis(n)
    ph = 2 * np.pi * f * t
    index = (0.4 + 1.6 * vel) * np.exp(-t / 0.25) + 0.35
    body = np.sin(ph + index * np.sin(ph))
    tine = np.sin(ph + 0.8 * vel * np.exp(-t / 0.02) * np.sin(14 * ph)) * np.exp(-t / 0.06)
    amp = np.exp(-t / (1.6 * (261.6 / f) ** 0.4)) * envelope(n, 0.002, 1, 1, release, gate)
    x = (body + 0.35 * vel * tine) * amp * (0.5 + 0.5 * vel)
    trem = 0.15 * np.sin(2 * np.pi * 4.2 * t + rng.uniform(0, 2 * np.pi))
    return np.stack([x * (1 + trem), x * (1 - trem)], axis=1)


def strum(voice, notes, gate, vel, spread=0.008, seed=0):
    """Play a chord with each note a few ms after the last, like a loose hand."""
    rng = np.random.default_rng(seed)
    parts = []
    for i, m in enumerate(notes):
        offset = samples(i * spread + abs(rng.normal(0, 0.002)))
        sound = voice(m, gate, vel * rng.uniform(0.85, 1.0), seed=seed + i)
        parts.append((offset, sound if sound.ndim == 2 else pan(sound)))
    out = np.zeros((max(o + len(p) for o, p in parts), 2))
    for o, p in parts:
        out[o:o + len(p)] += p
    return out


def pad(notes, gate, cutoff=1100, seed=0):
    """Detuned saws through a low-pass, slow in and slow out. Glue, not a lead."""
    rng = np.random.default_rng(seed)
    release = 1.6
    n = samples(gate + release)
    out = np.zeros((n, 2))
    for m in notes:
        f = hz(m)
        for cents, side in ((-9, 0), (0, None), (9, 1)):
            v = saw(np.full(n, f * 2 ** (cents / 1200)), max_hz=3000, phase0=rng.uniform(0, 2 * np.pi))
            if side is None:
                out += 0.7 * v[:, None]
            else:
                out[:, side] += v
    out = lowpass(out, cutoff)
    return out * envelope(n, 0.9, 1.0, 1.0, release, gate)[:, None] / len(notes)


def bass(midi, gate, vel=1.0, glide_from=None, glide=0.07):
    """Warm sub with a little growl in the mids so it still reads on laptop and phone
    speakers. glide_from slides in from another note."""
    f = hz(midi)
    release = 0.04
    n = samples(gate + release)
    t = time_axis(n)
    freq = np.full(n, f)
    if glide_from is not None:
        freq = f * (hz(glide_from) / f) ** np.exp(-t / (glide / 3))
    ph = phase(freq)
    x = np.tanh(1.6 * (np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph))) / 1.6
    growl = lowpass(saw(freq, max_hz=4000), 520) * np.exp(-t / 0.18) * 0.35
    return (x + growl) * envelope(n, 0.004, 0.4, 0.8, release, gate) * vel


# Soprano-ish formants, widened for high sung notes: (centre Hz, bandwidth Hz, gain)
VOWELS = {
    "a": ((800, 200, 1.0), (1150, 220, 0.5), (2900, 300, 0.25), (3900, 350, 0.1)),
    "e": ((400, 160, 1.0), (2000, 250, 0.3), (2800, 300, 0.15), (3600, 350, 0.08)),
    "o": ((450, 160, 1.0), (800, 200, 0.4), (2830, 300, 0.12), (3800, 350, 0.05)),
    "u": ((325, 140, 1.0), (700, 180, 0.25), (2700, 350, 0.06), (3800, 400, 0.03)),
}


def vox(midi, gate, vowels="oa", fall=0.0, vel=1.0, seed=0):
    """A sung 'ooh-ah' chop: a buzzy source through vowel formants, moving from the
    first vowel to the second, with a scoop in, vibrato and an optional fall-off in
    semitones."""
    rng = np.random.default_rng(seed)
    f = hz(midi)
    release = 0.07
    n = samples(gate + release)
    t = time_axis(n)
    cents = -45 * np.exp(-t / 0.025)
    cents += 16 * np.sin(2 * np.pi * 5.3 * t) * np.clip((t - 0.12) / 0.15, 0, 1)
    if fall:
        cents -= fall * 100 * np.clip((t - gate * 0.55) / (gate * 0.45 + release), 0, 1) ** 2
    freq = f * 2 ** (cents / 1200)
    src = saw(freq, max_hz=7000) + 0.05 * highpass(rng.standard_normal(n), 3000)

    def through(vowel):
        return sum(g * bandpass(src, c - bw / 2, c + bw / 2) for c, bw, g in VOWELS[vowel])

    morph = np.clip(t / max(gate, 0.05), 0, 1)
    x = through(vowels[0]) * (1 - morph) + through(vowels[-1]) * morph
    return normalise(x * envelope(n, 0.008, 0.3, 0.85, release, gate)) * vel


# Texture

def vinyl(n, seed=0, amount=1.0):
    """Record surface: fine crackle that differs per side, a few duller pops and a
    bed of hiss. n samples long and filtered around the loop."""
    rng = np.random.default_rng(seed)
    seconds = n / SR
    ticks = np.zeros((n, 2))
    for side in (0, 1):
        count = int(9 * seconds)
        np.add.at(ticks[:, side], rng.integers(0, n, count),
                  rng.exponential(1, count) * rng.choice((-1, 1), count))
    pops = np.zeros(n)
    count = int(0.5 * seconds)
    np.add.at(pops, rng.integers(0, n, count), rng.exponential(2, count) * rng.choice((-1, 1), count))
    hiss = rng.standard_normal((n, 2))
    out = (on_loop(ticks, lambda s: bandpass(s, 1200, 8000)) * 0.06
           + on_loop(pops, lambda s: lowpass(s, 1800, order=1))[:, None] * 0.1
           + on_loop(hiss, lambda s: bandpass(s, 2500, 10000)) * 0.004)
    return out * amount


# Second batch: more drums

def dusty_snare(seed=0):
    """Fat boom-bap snare: a low body, a dull rattle and plenty of sampler grit."""
    rng = np.random.default_rng(seed)
    n = samples(0.45)
    t = time_axis(n)
    body = (np.sin(2 * np.pi * 175 * t) * np.exp(-t / 0.07)
            + 0.4 * np.sin(2 * np.pi * 290 * t) * np.exp(-t / 0.04))
    rattle = bandpass(rng.standard_normal(n), 900, 5000) * np.exp(-t / 0.14)
    x = np.tanh(1.8 * (0.7 * body + 0.8 * rattle))
    return normalise(fade_out(crush(lowpass(x, 6000), bits=10, hold=3), 0.05))


def break_snare(seed=0):
    """Tight, bright snare for breakbeats."""
    rng = np.random.default_rng(seed)
    n = samples(0.3)
    t = time_axis(n)
    body = np.sin(2 * np.pi * 230 * t) * np.exp(-t / 0.04) + 0.5 * np.sin(2 * np.pi * 410 * t) * np.exp(-t / 0.025)
    snap = bandpass(rng.standard_normal(n), 1800, 9000) * np.exp(-t / 0.07)
    x = np.tanh(2.0 * (0.6 * body + 0.9 * snap))
    return normalise(fade_out(crush(x, bits=12, hold=2), 0.03))


def ride(seed=0):
    """Washy ride cymbal with a little bell ping."""
    rng = np.random.default_rng(seed)
    n = samples(1.2)
    t = time_axis(n)
    metal = np.zeros(n)
    for f in rng.uniform(2800, 7800, 24):
        metal += np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi))
    ping = np.sin(2 * np.pi * 3150 * t) * np.exp(-t / 0.12) * 0.6
    x = (metal / 5 + 0.4 * rng.standard_normal(n)) * np.exp(-t / 0.45)
    x = lowpass(highpass(x, 3000), 10000) + ping
    return normalise(fade_out(fade_in(x, 0.001), 0.2))


def rail_clack(seed=0):
    """A train wheel going over a rail joint: a dull thump with a metal edge."""
    rng = np.random.default_rng(seed)
    n = samples(0.25)
    t = time_axis(n)
    thump = np.sin(2 * np.pi * (70 + 40 * np.exp(-t / 0.01)) * t) * np.exp(-t / 0.06)
    clank = bandpass(rng.standard_normal(n), 400, 1800) * np.exp(-t / 0.03)
    ring = np.sin(2 * np.pi * 1230 * t) * np.exp(-t / 0.05) * 0.15
    return normalise(fade_out(0.8 * thump + 0.6 * clank + ring, 0.03))


def chip_noise(length=0.12, cutoff=8000, seed=0):
    """8-bit noise burst: short for hats, longer for snares."""
    rng = np.random.default_rng(seed)
    n = samples(length)
    t = time_axis(n)
    x = np.repeat(rng.choice((-1.0, 1.0), n // 4 + 1), 4)[:n]
    x = lowpass(x, cutoff) * np.exp(-t / (length / 4))
    return normalise(fade_out(crush(x, bits=5), 0.01))


# Second batch: tonal

def pluck(midi, gate, vel=0.8, seed=0, brightness=0.6, decay=2.5, position=0.14):
    """Karplus-Strong plucked string, a koto or nylon guitar depending on brightness.
    The feedback loop is worked out a period at a time, so it stays fast in numpy."""
    rng = np.random.default_rng(seed)
    period = SR / hz(midi)
    n = samples(gate + 0.15)
    # A three-tap filter in the loop: linear interpolation for the fractional part of
    # the period, followed by the usual two-sample average, which adds half a sample.
    size = int(np.floor(period - 0.5))
    frac = period - 0.5 - size
    loss = 10 ** (-3 / (decay * hz(midi)))
    taps = (loss * (1 - frac) / 2, loss / 2, loss * frac / 2)

    burst = rng.uniform(-1, 1, size + 2)
    burst = burst - np.roll(burst, max(1, int(position * size)))
    burst = lowpass(burst, 1200 + 8000 * brightness * vel, order=1)
    y = np.zeros(n)
    y[:size + 2] = burst
    start = size + 2
    while start < n:
        end = min(start + size, n)
        y[start:end] = (taps[0] * y[start - size:end - size]
                        + taps[1] * y[start - size - 1:end - size - 1]
                        + taps[2] * y[start - size - 2:end - size - 2])
        start = end

    y = y + 0.35 * bandpass(y, 1800, 3600)
    t = time_axis(n)
    damp = np.where(t < gate, 1.0, np.exp(-(t - gate) / 0.04))
    # A millisecond or two of attack keeps the noise burst from clicking
    return normalise(fade_out(fade_in(y * damp, 0.0015), 0.01)) * vel


def upright(midi, gate, vel=0.8):
    """Upright bass: a round plucked note that dies away, with a soft finger thump."""
    f = hz(midi)
    n = samples(gate + 0.08)
    t = time_axis(n)
    ph = 2 * np.pi * f * t
    x = np.sin(ph) + 0.3 * np.sin(2 * ph) * np.exp(-t / 0.25) + 0.1 * np.sin(3 * ph) * np.exp(-t / 0.12)
    thump = lowpass(np.random.default_rng(note(midi)).standard_normal(n), 400) * np.exp(-t / 0.015) * 0.6
    x = np.tanh(1.3 * (x * np.exp(-t / 0.7) + thump)) / 1.3
    return x * envelope(n, 0.005, 1, 1, 0.08, gate) * vel


def organ(midi, gate, vel=0.8, seed=0):
    """House organ stab: sine drawbars with fast-fading upper partials and a key click."""
    rng = np.random.default_rng(seed)
    f = hz(midi)
    release = 0.08
    n = samples(gate + release)
    t = time_axis(n)
    ph = 2 * np.pi * f * t
    x = (np.sin(ph) + 0.7 * np.sin(2 * ph) + 0.45 * np.sin(3 * ph)
         + 0.35 * np.sin(4 * ph) * np.exp(-t / 0.15)
         + 0.25 * np.sin(6 * ph) * np.exp(-t / 0.08)
         + 0.15 * np.sin(8 * ph) * np.exp(-t / 0.05))
    click = highpass(rng.standard_normal(n), 2000) * np.exp(-t / 0.003) * 0.4
    return (x / 2.5 + click) * envelope(n, 0.003, 0.25, 0.65, release, gate) * vel


def chip(midi, gate, vel=0.8, duty=0.25, vibrato=0.0, slide_from=None):
    """Square-wave lead in the style of an old console, with delayed vibrato."""
    f = hz(midi)
    n = samples(gate + 0.03)
    t = time_axis(n)
    cents = vibrato * 25 * np.sin(2 * np.pi * 6 * t) * np.clip((t - 0.15) / 0.1, 0, 1)
    freq = f * 2 ** (cents / 1200)
    if slide_from is not None:
        freq = freq * (hz(slide_from) / f) ** np.exp(-t / 0.02)
    return pulse(freq, duty) * envelope(n, 0.002, 0.15, 0.7, 0.03, gate) * vel * 0.5


def chip_arp(notes, gate, rate, vel=0.6, duty=0.125):
    """Fast arpeggio cycling through chord notes, the classic way old consoles faked chords."""
    n = samples(gate + 0.02)
    t = time_axis(n)
    freqs = np.array([hz(m) for m in notes])
    freq = freqs[(t / rate).astype(int) % len(freqs)]
    return pulse(freq, duty) * envelope(n, 0.002, 0.2, 0.8, 0.02, gate) * vel * 0.5


def reese(midi, gate, vel=1.0, cutoff=(280, 900), seed=0):
    """Drum and bass reese: detuned saws beating against each other, with the filter
    opening and closing slowly across the note."""
    rng = np.random.default_rng(seed)
    f = hz(midi)
    n = samples(gate + 0.08)
    t = time_axis(n)
    x = sum(saw(np.full(n, f * 2 ** (cents / 1200)), max_hz=3000, phase0=rng.uniform(0, 2 * np.pi))
            for cents in (-14, 0, 13)) / 2.5
    sweep = 0.5 - 0.5 * np.cos(2 * np.pi * t / max(gate, 0.5))
    dark, bright = lowpass(x, cutoff[0]), lowpass(x, cutoff[1])
    x = np.tanh(1.5 * (dark + (bright - dark) * sweep)) / 1.5
    return highpass(x, 110) * envelope(n, 0.01, 0.3, 0.9, 0.08, gate) * vel


def flute(midi, gate, vel=0.8, seed=0):
    """Breathy bamboo flute: a soft tone with air in it, bending up into the note and
    gaining vibrato as it's held."""
    rng = np.random.default_rng(seed)
    f = hz(midi)
    release = 0.12
    n = samples(gate + release)
    t = time_axis(n)
    cents = -70 * np.exp(-t / 0.06) + 18 * np.sin(2 * np.pi * 5 * t) * np.clip((t - 0.25) / 0.4, 0, 1)
    ph = phase(f * 2 ** (cents / 1200))
    tone = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    air = bandpass(rng.standard_normal(n), f * 0.8, min(f * 3, 9000), order=1)
    breath = 0.35 + 0.65 * np.exp(-t / 0.08)
    x = tone + air * 0.35 * breath / max(np.std(air), 1e-9) * 0.2
    return normalise(x * envelope(n, 0.06, 0.4, 0.85, release, gate)) * vel


def bell(midi, gate, vel=0.7, seed=0):
    """Glassy FM bell, like a toy celesta."""
    f = hz(midi)
    n = samples(gate + 1.2)
    t = time_axis(n)
    index = 2.2 * np.exp(-t / 0.4) + 0.3
    x = np.sin(2 * np.pi * f * t + index * np.sin(2 * np.pi * 3.5 * f * t))
    x += 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.3)
    return x * np.exp(-t / 1.1) * envelope(n, 0.002, 1, 1, 0.6, gate + 0.6) * vel * 0.6


# Second batch: textures

def rain(n, seed=0, amount=1.0):
    """Soft rain on a window: a hiss that swells and eases, with droplets ticking
    through it. n samples long, filtered around the loop."""
    rng = np.random.default_rng(seed)
    seconds = n / SR
    t = time_axis(n)
    cycles = max(1, round(seconds / 9))
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * cycles * t / seconds)
    bed = on_loop(rng.standard_normal((n, 2)), lambda s: lowpass(highpass(s, 500), 6000)) * 0.03
    drops = np.zeros((n, 2))
    for side in (0, 1):
        count = int(30 * seconds)
        np.add.at(drops[:, side], rng.integers(0, n, count), rng.exponential(1, count))
    drops = on_loop(drops, lambda s: bandpass(s, 1500, 7000)) * 0.05
    return (bed * swell[:, None] + drops) * amount


def rumble(n, seed=0, amount=1.0):
    """Low carriage rumble: brown-ish noise under 150 Hz, breathing slowly."""
    rng = np.random.default_rng(seed)
    seconds = n / SR
    t = time_axis(n)
    cycles = max(1, round(seconds / 11))
    swell = 0.7 + 0.3 * np.sin(2 * np.pi * cycles * t / seconds)
    x = on_loop(rng.standard_normal(n), lambda s: lowpass(highpass(s, 30), 150, order=2))
    return pan(x / max(np.std(x), 1e-9) * 0.05 * swell * amount)


# Third batch: band instruments for the sunnier tracks

def clap(seed=0):
    """Hand clap on its own, slightly crunched."""
    rng = np.random.default_rng(seed)
    n = samples(0.4)
    t = time_axis(n)
    return normalise(fade_out(crush(_clap(rng, n, t), bits=12, hold=2), 0.03))


def conga(high=True, slap=False, seed=0):
    """Hand drum: a tuned skin with a pitch drop. Slaps are shorter and brighter."""
    rng = np.random.default_rng(seed)
    n = samples(0.35)
    t = time_axis(n)
    base = 330 if high else 220
    tone = np.sin(phase(base * (1 + 0.12 * np.exp(-t / 0.015)))) * np.exp(-t / (0.06 if slap else 0.16))
    skin = bandpass(rng.standard_normal(n), 1500 if slap else 600, 6000 if slap else 2500) * np.exp(-t / 0.012)
    x = tone + skin * (1.2 if slap else 0.4)
    return normalise(fade_out(x, 0.03))


def brush(seed=0):
    """Brushed snare: a soft swish with a slow-ish attack."""
    rng = np.random.default_rng(seed)
    n = samples(0.3)
    t = time_axis(n)
    x = bandpass(rng.standard_normal(n), 1500, 7000) * (1 - np.exp(-t / 0.012)) * np.exp(-t / 0.09)
    x += 0.3 * np.sin(2 * np.pi * 200 * t) * np.exp(-t / 0.04)
    return normalise(fade_out(x, 0.03))


def strum_guitar(notes, gate, down=True, vel=0.8, spread=0.011, seed=0, brightness=0.55, decay=2.0):
    """A strum across guitar strings, low to high on a downstroke and high to low on an
    upstroke. Every string is a Karplus-Strong pluck."""
    rng = np.random.default_rng(seed)
    order = list(notes) if down else list(reversed(notes))
    parts = []
    for i, m in enumerate(order):
        offset = samples(i * spread * rng.uniform(0.8, 1.2))
        # Strings further along the stroke are hit a little softer
        v = vel * (1 - 0.06 * i) * rng.uniform(0.9, 1.0)
        parts.append((offset, pluck(m, max(0.03, gate - i * spread), v, seed=seed + i,
                                    brightness=brightness, decay=decay)))
    out = np.zeros(max(o + len(p) for o, p in parts))
    for o, p in parts:
        out[o:o + len(p)] += p
    return out / max(1.0, len(notes) ** 0.5)


def brass(midi, gate, vel=0.8, seed=0):
    """Synth horn: detuned saws with a filter that bites on the attack and settles."""
    rng = np.random.default_rng(seed)
    f = hz(midi)
    release = 0.08
    n = samples(gate + release)
    t = time_axis(n)
    freq = f * 2 ** ((-40 * np.exp(-t / 0.03)) / 1200)
    x = sum(saw(freq * 2 ** (c / 1200), max_hz=8000, phase0=rng.uniform(0, 2 * np.pi)) for c in (-6, 6)) / 2
    bite = np.exp(-t / 0.12)
    dark, bright = lowpass(x, f * 2.5), lowpass(x, min(f * 10, 9000))
    x = dark + (bright - dark) * (0.35 + 0.65 * bite)
    return np.tanh(1.4 * x) * envelope(n, 0.015, 0.2, 0.75, release, gate) * vel


def melodica(midi, gate, vel=0.8, seed=0):
    """Reedy little keyboard harmonica: a narrow pulse, softened, with breath and a
    slight wobble."""
    rng = np.random.default_rng(seed)
    f = hz(midi)
    release = 0.06
    n = samples(gate + release)
    t = time_axis(n)
    cents = 8 * np.sin(2 * np.pi * 4.5 * t) * np.clip((t - 0.2) / 0.3, 0, 1)
    x = pulse(f * 2 ** (cents / 1200), 0.3, max_hz=6000)
    x = lowpass(x, 2800) + 0.06 * bandpass(rng.standard_normal(n), 1500, 6000)
    return normalise(x * envelope(n, 0.03, 0.3, 0.85, release, gate)) * vel


def marimba(midi, gate, vel=0.8):
    """Wooden mallet bar: a fundamental with a short fourth-partial knock."""
    f = hz(midi)
    n = samples(gate + 0.5)
    t = time_axis(n)
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.45)
         + 0.45 * np.sin(2 * np.pi * 3.93 * f * t) * np.exp(-t / 0.05)
         + 0.2 * np.sin(2 * np.pi * 9.2 * f * t) * np.exp(-t / 0.012))
    return fade_out(fade_in(x, 0.001), 0.05) * vel * 0.7


def waves(n, seed=0, amount=1.0):
    """Gentle surf: washes of filtered noise rolling in and out, a whole number of
    times per loop."""
    rng = np.random.default_rng(seed)
    seconds = n / SR
    t = time_axis(n)
    cycles = max(1, round(seconds / 7))
    roll = 0.5 - 0.5 * np.cos(2 * np.pi * cycles * t / seconds)
    wash = on_loop(rng.standard_normal((n, 2)), lambda s: lowpass(highpass(s, 150), 2500))
    hiss = on_loop(rng.standard_normal((n, 2)), lambda s: bandpass(s, 2500, 8000))
    x = wash * (0.03 + 0.08 * roll ** 2)[:, None] + hiss * (0.01 * roll ** 3)[:, None]
    return x * amount
