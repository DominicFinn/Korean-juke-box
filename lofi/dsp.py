"""Signal building blocks: oscillators, envelopes, filters and loop-safe effects.

Everything is float64 numpy at SR. Mono is shape (n,), stereo is (n, 2).

Effects with memory (filters, reverb, delay, tape wobble) run so the loop's own end
feeds its start. That's what keeps a rendered loop free of clicks and cut-off tails
at the seam.
"""
from functools import lru_cache

import numpy as np
import pyloudnorm
from scipy import fft, signal

SR = 44100

_LETTERS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def note(name):
    """'F2', 'Eb4' or 'C#5' to a MIDI number. Ints pass straight through."""
    if isinstance(name, (int, np.integer)):
        return int(name)
    semis = _LETTERS[name[0].upper()]
    i = 1
    while name[i] in "#b":
        semis += 1 if name[i] == "#" else -1
        i += 1
    return 12 * (int(name[i:]) + 1) + semis


def hz(midi):
    return 440.0 * 2 ** ((note(midi) - 69) / 12)


def samples(seconds):
    return int(round(seconds * SR))


def time_axis(n):
    return np.arange(n) / SR


def phase(freq):
    """Running phase in radians for a per-sample frequency array."""
    return 2 * np.pi * np.concatenate(([0.0], np.cumsum(freq[:-1]))) / SR


# Oscillators

def saw(freq, max_hz=8000, phase0=0.0):
    """Band-limited saw built from harmonics up to max_hz, so it doesn't alias."""
    ph = phase(freq) + phase0
    out = np.zeros_like(ph)
    for k in range(1, max(1, int(max_hz // np.max(freq))) + 1):
        out += np.sin(k * ph) / k
    return out * (2 / np.pi)


def pulse(freq, duty=0.5, max_hz=9000, phase0=0.0):
    """Band-limited pulse wave: two saws offset by the duty cycle. 0.5 is a square,
    0.25 and 0.125 are the thinner NES-style tones."""
    x = saw(freq, max_hz, phase0) - saw(freq, max_hz, phase0 + 2 * np.pi * duty)
    return x - np.mean(x)


def stepped_triangle(freq, steps=16):
    """Triangle quantised to a few levels, like the NES bass channel."""
    tri = 2 / np.pi * np.arcsin(np.sin(phase(freq)))
    return np.round(tri * steps / 2) / (steps / 2)


# Envelopes and gain

def fade_in(x, seconds):
    k = min(len(x), samples(seconds))
    ramp = np.linspace(0, 1, k)
    x = x.copy()
    x[:k] *= ramp if x.ndim == 1 else ramp[:, None]
    return x


def fade_out(x, seconds):
    k = min(len(x), samples(seconds))
    ramp = np.linspace(1, 0, k)
    x = x.copy()
    x[len(x) - k:] *= ramp if x.ndim == 1 else ramp[:, None]
    return x


def envelope(n, attack, decay, sustain, release, gate):
    """ADSR with exponential decay and release. gate is how long the note is held in
    seconds; the buffer should be about gate + release long."""
    t = time_axis(n)
    env = np.where(
        t < attack,
        t / max(attack, 1e-4),
        sustain + (1 - sustain) * np.exp(-(t - attack) / max(decay, 1e-4)),
    )
    held = t >= gate
    if held.any():
        g = int(np.argmax(held))
        env[g:] = env[g] * np.exp(-(t[g:] - gate) / max(release / 4, 1e-4))
    return fade_out(env, 0.004)


def normalise(x, peak=1.0):
    top = np.max(np.abs(x))
    return x * (peak / top) if top > 0 else x


def pan(mono, position=0.0):
    """Constant-power pan, -1 left to 1 right. Centre leaves each side at unity."""
    angle = (position + 1) * np.pi / 4
    return np.stack([mono * np.cos(angle), mono * np.sin(angle)], axis=1) * np.sqrt(2)


def balance(stereo, position=0.0):
    return stereo * np.array([min(1.0, 1 - position), min(1.0, 1 + position)])


# Filters

@lru_cache(maxsize=256)
def _butter(kind, cutoff, order):
    return signal.butter(order, cutoff, btype=kind, fs=SR, output="sos")


def lowpass(x, cutoff, order=2):
    return signal.sosfilt(_butter("lowpass", float(cutoff), order), x, axis=0)


def highpass(x, cutoff, order=2):
    return signal.sosfilt(_butter("highpass", float(cutoff), order), x, axis=0)


def bandpass(x, lo, hi, order=1):
    return signal.sosfilt(_butter("bandpass", (float(lo), float(hi)), order), x, axis=0)


# Colour

def saturate(x, drive=1.5):
    """tanh warmth. Quiet signals pass at unity, peaks get rounded off."""
    return np.tanh(drive * x) / drive


def crush(x, bits=12, hold=1):
    """Sampler grit: fewer bits, and a sample-and-hold to fake a lower sample rate."""
    if hold > 1:
        x = np.repeat(x[::hold], hold, axis=0)[: len(x)]
    step = 2.0 ** (1 - bits)
    return np.round(x / step) * step


def soft_clip(x, ceiling=0.89, knee=0.75):
    """Linear up to knee * ceiling, then curves smoothly into the ceiling."""
    t = ceiling * knee
    a = np.abs(x)
    over = a > t
    y = x.copy()
    y[over] = np.sign(x[over]) * (t + (ceiling - t) * np.tanh((a[over] - t) / (ceiling - t)))
    return y


# Loop-safe effects

def moving_lowpass(x, curve, lo, hi, steps=8):
    """Low-pass whose cutoff follows `curve` (0 to 1 per sample, log-spaced from lo to
    hi). Renders a handful of fixed cutoffs around the loop and blends between them."""
    cutoffs = np.geomspace(lo, hi, steps)
    versions = [on_loop(x, lambda s, c=c: lowpass(s, c)) for c in cutoffs]
    pos = np.clip(curve, 0, 1) * (steps - 1)
    i0 = np.minimum(np.floor(pos).astype(int), steps - 2)
    frac = pos - i0
    if x.ndim == 2:
        frac = frac[:, None]
    out = np.zeros_like(x)
    for i in range(steps - 1):
        here = i0 == i
        if here.any():
            out[here] = versions[i][here] * (1 - frac[here]) + versions[i + 1][here] * frac[here]
    return out


def on_loop(x, effect):
    """Run a causal effect over two copies of the loop and keep the second, so the
    effect's state at the start comes from the loop's own end."""
    n = len(x)
    return effect(np.concatenate([x, x], axis=0))[n:]


def loop_convolve(x, ir):
    """Circular convolution. Tails that run past the end wrap round to the start."""
    n = len(x)
    folded = np.zeros((n,) + ir.shape[1:])
    for start in range(0, len(ir), n):
        chunk = ir[start:start + n]
        folded[: len(chunk)] += chunk
    if x.ndim == 1 and folded.ndim == 2:
        x = x[:, None]
    if x.ndim == 2 and folded.ndim == 1:
        folded = folded[:, None]
    return fft.irfft(fft.rfft(x, axis=0) * fft.rfft(folded, axis=0), n=n, axis=0)


def reverb_ir(seconds=2.4, predelay=0.02, brightness=6000, seed=1):
    """Stereo impulse response of decaying noise that gets darker as it fades.
    Normalised to unit energy, so the wet level is roughly the send level."""
    rng = np.random.default_rng(seed)
    n = samples(seconds)
    t = time_axis(n)
    noise = rng.standard_normal((n, 2)) * np.exp(-t * 6.9 / seconds)[:, None]
    bright, dark = lowpass(noise, brightness), lowpass(noise, brightness * 0.3)
    mix = np.exp(-t / (seconds * 0.2))[:, None]
    ir = highpass(bright * mix + dark * (1 - mix), 180)
    ir = fade_in(ir, 0.008)
    ir = np.concatenate([np.zeros((samples(predelay), 2)), ir])
    return ir / np.sqrt(np.sum(ir ** 2) / 2)


def delay_ir(delay_s, feedback=0.4, repeats=6, damping=3500):
    """Ping-pong echo as an impulse response. Each repeat swaps sides and gets duller,
    like a feedback delay with a filter in the loop."""
    d = samples(delay_s)
    kernel = 512
    ir = np.zeros((d * repeats + kernel, 2))
    tap = np.zeros(kernel)
    tap[0] = 1.0
    for k in range(1, repeats + 1):
        tap = lowpass(tap, damping, order=1)
        ir[k * d:k * d + kernel, (k - 1) % 2] += tap * feedback ** (k - 1)
    return highpass(ir, 300)


def tape_wobble(x, wow_hz=0.4, wow_ms=0.9, flutter_hz=5.5, flutter_ms=0.05):
    """Worn-tape pitch drift: slow wow and fast flutter from a moving read point.
    Rates snap to whole cycles per loop so the wobble lines up at the seam."""
    n = len(x)
    seconds = n / SR

    def snap(rate):
        return max(1, round(rate * seconds)) / seconds

    t = time_axis(n)
    delay_ms = (wow_ms * (1 + np.sin(2 * np.pi * snap(wow_hz) * t))
                + flutter_ms * (1 + np.sin(2 * np.pi * snap(flutter_hz) * t + 1.3)))
    pos = np.arange(n) - delay_ms * SR / 1000
    i0 = np.floor(pos).astype(int)
    frac = pos - i0
    if x.ndim == 2:
        frac = frac[:, None]
    return x[i0 % n] * (1 - frac) + x[(i0 + 1) % n] * frac


def duck(n, hits, depth=0.5, release=0.15, attack=0.004):
    """Sidechain gain curve: dips by `depth` at each hit (in samples) and recovers."""
    k = samples(release * 5)
    t = time_axis(k)
    shape = (1 - np.exp(-t / attack)) * np.exp(-t / release)
    shape /= shape.max()
    amount = np.zeros(n)
    for start in hits:
        idx = (start + np.arange(k)) % n
        amount[idx] = np.maximum(amount[idx], shape)
    return (1 - depth * amount)[:, None]


# Mastering

def master(x, lufs=-16.0, ceiling_db=-1.0):
    """Trim the extremes, set loudness to `lufs` and soft-clip peaks under the ceiling.
    Holding every track to the same loudness keeps the series consistent in a game."""
    x = on_loop(x, lambda s: lowpass(highpass(s, 30), 12000))
    meter = pyloudnorm.Meter(SR)
    ceiling = 10 ** (ceiling_db / 20)
    gain = 1.0
    for _ in range(3):
        out = soft_clip(x * gain, ceiling)
        gain *= 10 ** ((lufs - meter.integrated_loudness(out)) / 20)
    return soft_clip(x * gain, ceiling)
