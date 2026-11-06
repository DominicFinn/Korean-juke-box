"""Render the loops in tracks/ to out/ as WAV (with loop points) and OGG Vorbis.

    .venv/bin/python render.py                     every track
    .venv/bin/python render.py night_bus           one track
    .venv/bin/python render.py night_bus --preview also write three loops back to back
    .venv/bin/python render.py night_bus --levels  show how loud each part is in the mix
"""
import argparse
import importlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import soundfile

from lofi.dsp import SR

ROOT = Path(__file__).parent
OUT = ROOT / "out"


def write_wav(path, x):
    """16-bit stereo WAV with a 'smpl' chunk marking the whole file as a forward loop.
    Godot, FMOD, Wwise and most samplers pick the loop points up from it."""
    dither = (np.random.default_rng(0).random(x.shape) - np.random.default_rng(1).random(x.shape)) / 32768
    pcm = np.clip(np.round((x + dither) * 32767), -32768, 32767).astype("<i2")
    data = pcm.tobytes()
    frames = len(x)
    fmt = struct.pack("<HHIIHH", 1, 2, SR, SR * 4, 4, 16)
    smpl = struct.pack("<9I", 0, 0, round(1e9 / SR), 60, 0, 0, 0, 1, 0)
    smpl += struct.pack("<6I", 0, 0, 0, frames - 1, 0, 0)
    chunks = b"".join(tag + struct.pack("<I", len(body)) + body
                      for tag, body in ((b"fmt ", fmt), (b"data", data), (b"smpl", smpl)))
    path.write_bytes(b"RIFF" + struct.pack("<I", 4 + len(chunks)) + b"WAVE" + chunks)


def update_manifest(name, info, frames):
    """Keep out/tracks.json listing every rendered loop, for the jukebox app. Tracks keep
    their place in the list when re-rendered and new ones go on the end."""
    path = OUT / "tracks.json"
    tracks = json.loads(path.read_text())["tracks"] if path.exists() else []
    entry = {"name": name, "file": f"{name}.wav", "seconds": round(frames / SR, 4), **info}
    existing = [i for i, t in enumerate(tracks) if t["name"] == name]
    if existing:
        tracks[existing[0]] = entry
    else:
        tracks.append(entry)
    path.write_text(json.dumps({"tracks": tracks}, ensure_ascii=False, indent=2) + "\n")


def db(x):
    return 20 * np.log10(max(x, 1e-12))


def rms(x):
    return float(np.sqrt(np.mean(x ** 2)))


def render(name, preview=False, levels=False):
    module = importlib.import_module(f"tracks.{name}")
    info = module.TRACK
    mix, parts = module.build()

    OUT.mkdir(exist_ok=True)
    write_wav(OUT / f"{name}.wav", mix)
    soundfile.write(OUT / f"{name}.ogg", mix, SR, format="OGG", subtype="VORBIS", compression_level=0.3)
    update_manifest(name, info, len(mix))
    if preview:
        (OUT / "preview").mkdir(exist_ok=True)
        write_wav(OUT / "preview" / f"{name}_x3.wav", np.concatenate([mix] * 3))

    # The jump from the last sample back to the first should look like any other step
    steps = np.abs(np.diff(mix, axis=0))
    seam = float(np.max(np.abs(mix[0] - mix[-1])))
    print(f"{info['title']}: {info['bpm']} BPM, {info['bars']} bars, {info['key']}, {len(mix) / SR:.2f}s")
    print(f"  peak {db(np.max(np.abs(mix))):.1f} dBFS, rms {db(rms(mix)):.1f} dBFS")
    print(f"  seam step {seam:.4f} (largest step anywhere {np.max(steps):.4f}, 99.9th pct {np.percentile(steps, 99.9):.4f})")
    if levels:
        total = rms(sum(parts.values()))
        for part, x in parts.items():
            print(f"  {part:>7} {db(rms(x) / total):6.1f} dB")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tracks", nargs="*")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--levels", action="store_true")
    args = parser.parse_args()
    names = args.tracks or sorted(p.stem for p in (ROOT / "tracks").glob("*.py") if p.stem != "__init__")
    sys.path.insert(0, str(ROOT))
    for name in names:
        render(name, args.preview, args.levels)


if __name__ == "__main__":
    main()
