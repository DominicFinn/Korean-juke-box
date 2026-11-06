import numpy as np

from .dsp import SR, balance, pan, samples


class Song:
    """A fixed-length loop on a 16th-note grid. Sounds go onto named stereo buses and
    anything that runs past the end wraps round to the start, so the loop joins up."""

    def __init__(self, bpm, bars, swing=0.5, seed=0):
        self.bpm = bpm
        self.bars = bars
        self.swing = swing
        self.step_s = 60 / bpm / 4
        self.length = samples(bars * 16 * self.step_s)
        self.rng = np.random.default_rng(seed)
        self.buses = {}

    @property
    def seconds(self):
        return self.length / SR

    def at(self, bar, step=0, swing=None, jitter_ms=0.0):
        """Seconds from the loop start for a 16th-note step. Off-beat 16ths are pushed
        late by the swing amount (0.5 is straight, around 0.6 is a garage shuffle)."""
        swing = self.swing if swing is None else swing
        t = (bar * 16 + step) * self.step_s
        if float(step).is_integer() and int(step) % 2 == 1:
            t += (swing - 0.5) * 2 * self.step_s
        if jitter_ms:
            t += self.rng.normal(0, jitter_ms / 1000)
        return t

    def bus(self, name):
        if name not in self.buses:
            self.buses[name] = np.zeros((self.length, 2))
        return self.buses[name]

    def add(self, name, sound, t, gain=1.0, pan_to=0.0):
        sound = pan(sound, pan_to) if sound.ndim == 1 else balance(sound, pan_to)
        sound = sound * gain
        buf = self.bus(name)
        pos = samples(t) % self.length
        i = 0
        while i < len(sound):
            chunk = min(len(sound) - i, self.length - pos)
            buf[pos:pos + chunk] += sound[i:i + chunk]
            i += chunk
            pos = 0
