"""Tools for building tracks from real recordings dropped into inbox/: load any audio
ffmpeg can read, find the sung phrases, track pitch, work out tuning and key, and nudge
the recording to concert pitch."""
import subprocess

import numpy as np
from scipy import signal

from .dsp import SR

NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def load(path):
    """Any audio or video file, as mono float at SR, peak-normalised."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        check=True, capture_output=True,
    ).stdout
    x = np.frombuffer(raw, dtype="<f4").astype(np.float64)
    return x / (np.max(np.abs(x)) + 1e-12)


def pitch(x, hop=441, window=2048, fmin=100, fmax=900, threshold=0.15):
    """YIN pitch tracking. Returns MIDI note numbers per hop, NaN where unvoiced."""
    frames = max(0, (len(x) - window) // hop)
    longest = int(SR / fmin) + 1
    shortest = int(SR / fmax)
    half = window // 2
    midi = np.full(frames, np.nan)
    for i in range(frames):
        seg = x[i * hop:i * hop + window]
        if np.sqrt(np.mean(seg ** 2)) < 0.03:
            continue
        head = seg[:half]
        corr = signal.fftconvolve(seg, head[::-1], mode="valid")[:longest]
        energy = np.cumsum(seg ** 2)
        shifted = energy[half - 1:half - 1 + longest] - np.concatenate(([0], energy[:longest - 1]))
        diff = np.sum(head ** 2) + shifted - 2 * corr
        diff[0] = 0
        norm = np.ones_like(diff)
        norm[1:] = diff[1:] * np.arange(1, len(diff)) / (np.cumsum(diff[1:]) + 1e-12)
        below = np.where(norm[shortest:] < threshold)[0]
        if not len(below):
            continue
        tau = below[0] + shortest
        while tau + 1 < len(norm) and norm[tau + 1] < norm[tau]:
            tau += 1
        if 1 <= tau < len(norm) - 1:
            a, b, c = norm[tau - 1], norm[tau], norm[tau + 1]
            tau += 0.5 * (a - c) / (a - 2 * b + c + 1e-12)
        midi[i] = 69 + 12 * np.log2(SR / tau / 440)
    return midi


def tuning(midi):
    """How far the singer sits from concert pitch, in cents (negative is flat)."""
    voiced = midi[~np.isnan(midi)]
    offsets = (voiced - np.round(voiced)) * 100
    # Circular median, so notes sung a little sharp and a little flat don't cancel oddly
    angle = np.angle(np.mean(np.exp(1j * offsets / 100 * 2 * np.pi)))
    return angle / (2 * np.pi) * 100


def key(midi):
    """Best-fitting key from how long each pitch class is sung (Krumhansl profiles)."""
    voiced = midi[~np.isnan(midi)]
    counts = np.bincount(np.round(voiced).astype(int) % 12, minlength=12).astype(float)
    major = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    score, name = max((np.corrcoef(np.roll(profile, k), counts)[0, 1], f"{NOTE_NAMES[k]} {mode}")
                      for k in range(12) for profile, mode in ((major, "major"), (minor, "minor")))
    return name


def retune(x, cents):
    """Shift pitch by resampling, like speeding a tape up. It changes the length by the same
    small ratio, which is fine for a few tens of cents."""
    ratio = 2 ** (cents / 1200)
    return signal.resample(x, int(round(len(x) / ratio)))


def phrases(x, quiet_db=-30, smooth=0.15, shortest=0.4):
    """Start and end samples of each sung phrase, split at the breaths between them. The
    start is the first moment it gets loud, so it lines up with the first syllable."""
    hop = 441
    level = np.array([np.sqrt(np.mean(x[i:i + 1024] ** 2)) for i in range(0, len(x) - 1024, hop)])
    db = 20 * np.log10(level + 1e-9)
    loud = db > quiet_db
    k = max(1, int(smooth * SR / hop))
    active = np.convolve(loud.astype(float), np.ones(k) / k, mode="same") > 0.3
    edges = np.diff(np.concatenate(([0], active.astype(int), [0])))
    result = []
    for start, end in zip(np.where(edges == 1)[0], np.where(edges == -1)[0]):
        if (end - start) * hop / SR < shortest:
            continue
        # Walk forward from the smoothed edge to the first genuinely loud frame
        first = start + int(np.argmax(loud[start:end]))
        result.append((first * hop, min(len(x), end * hop + hop)))
    return result


def note_name(midi):
    m = int(round(midi))
    return f"{NOTE_NAMES[m % 12]}{m // 12 - 1}"


MAJOR_STEPS = (0, 2, 4, 5, 7, 9, 11)


def transcribe(x, bar_seconds, starts, tonic="A", steps_per_bar=16):
    """Turn a sung recording into notes: one list per phrase of (step, length in steps,
    MIDI note), with the phrase start as step 0. A new note starts at each syllable, the
    pitch is the median sung pitch until the next one, stray octaves are folded back
    towards the singer's usual range, and every note is snapped to the major scale."""
    hop = 441
    midi = pitch(x, hop=hop, fmin=90, fmax=600, threshold=0.25)
    centre = np.nanmedian(midi)
    folded = midi.copy()
    far = ~np.isnan(folded) & (np.abs(folded - centre) > 7)
    folded[far] -= 12 * np.round((folded[far] - centre) / 12)

    # Syllable onsets from positive spectral change, at least 90 ms apart
    f, t, Z = signal.stft(x, SR, nperseg=1024, noverlap=1024 - hop)
    mag = np.log1p(np.abs(Z) * 50)
    flux = np.maximum(0, np.diff(mag, axis=1)).sum(axis=0)
    flux = np.maximum(0, flux - np.convolve(flux, np.ones(25) / 25, mode="same"))
    onset_frames, _ = signal.find_peaks(flux, height=np.percentile(flux, 75), distance=9)
    level = np.array([np.sqrt(np.mean(x[i * hop:i * hop + 1024] ** 2)) for i in range(len(folded))])

    root = NOTE_NAMES.index(tonic)
    scale = [(root + s) % 12 for s in MAJOR_STEPS]

    def snap(m):
        candidates = [n for n in range(int(m) - 2, int(m) + 3) if n % 12 in scale]
        return min(candidates, key=lambda n: abs(n - m))

    step_seconds = bar_seconds / steps_per_bar
    result = []
    for start in starts:
        begin, finish = start, start + bar_seconds
        frames = [int(o) for o in onset_frames if begin - 0.06 <= o * hop / SR < finish - 0.1]
        notes = {}
        for k, first in enumerate(frames):
            last = frames[k + 1] if k + 1 < len(frames) else min(len(folded), int(finish * SR / hop))
            sung = folded[first:last]
            voiced = sung[~np.isnan(sung)]
            if len(voiced) < max(3, 0.3 * (last - first)):
                continue
            # The note lasts while it's still loud, up to the next syllable
            peak = level[first:last].max()
            loud = np.where(level[first:last] > peak * 0.25)[0]
            end = first + (loud[-1] + 1 if len(loud) else last - first)
            step = int(round((first * hop / SR - begin) / step_seconds))
            if not 0 <= step < steps_per_bar:
                continue
            length = max(1, int(round((end - first) * hop / SR / step_seconds)))
            note = snap(float(np.median(voiced)))
            if step not in notes or length > notes[step][0]:
                notes[step] = (min(length, steps_per_bar - step), note)
        result.append([(step, length, note) for step, (length, note) in sorted(notes.items())])
    return result
