#!/usr/bin/env python3
"""Synthesize the demo clip: a formant-synthesized adult voice singing a public-domain hymn.

No recording of any person is used. Writes three files next to --out:
  <name>.wav          the audio (the only thing analysis needs, besides lyric text)
  <name>.lyrics.json  syllables and phones, without any timing
  <name>.truth.json   the synthesizer's own pitch and notes, read only by evaluate.py
"""
import argparse
import json
from pathlib import Path

import numba
import numpy as np
import scipy.ndimage as ndi
import scipy.signal as sig
import soundfile as sf

SR_OUT = 44100
OVERSAMPLE = 2
SR = SR_OUT * OVERSAMPLE
CTRL_SR = 1000
BPM = 84
TRANSPOSE = -2  # the score below is written in G; the clip sounds in F

NOTE_INDEX = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(name):
    return 12 * (int(name[1]) + 1) + NOTE_INDEX[name[0]] + TRANSPOSE


# Syllable: grapheme, pronunciation respelling, phones, [(note, beats), ...], rest beats after.
# Melody and text after the traditional hymn "Amazing Grace" (text J. Newton, 1779; tune
# New Britain, 1829). The note-for-note arrangement here is this program's own.
SCORE = [
    ("A", "uh", ["AH"], [("D4", 1)], 0),
    ("ma", "may", ["M", "EY"], [("G4", 2), ("B4", .5), ("G4", .5)], 0),
    ("zing", "zing", ["Z", "IH", "NG"], [("B4", 2), ("A4", 1)], 0),
    ("grace", "grayss", ["G", "R", "EY", "S"], [("G4", 2)], 0),
    ("how", "how", ["HH", "AW"], [("E4", 1)], 0),
    ("sweet", "sweet", ["S", "W", "IY", "T"], [("D4", 2)], 0),
    ("the", "thuh", ["DH", "AH"], [("D4", 1)], 0),
    ("sound", "sownd", ["S", "AW", "N", "D"], [("G4", 2), ("B4", .5), ("G4", .5)], 1),
    ("that", "that", ["DH", "AE", "T"], [("B4", 2)], 0),
    ("saved", "sayvd", ["S", "EY", "V", "D"], [("A4", 1)], 0),
    ("a", "uh", ["AH"], [("B4", 1)], 0),
    ("wretch", "retch", ["R", "EH", "CH"], [("D5", 2)], 0),
    ("like", "lyke", ["L", "AY", "K"], [("B4", 1)], 0),
    ("me", "mee", ["M", "IY"], [("D5", 4)], 1.5),
    ("I", "eye", ["AY"], [("B4", 1)], 0),
    ("once", "wunss", ["W", "AH", "N", "S"], [("D5", 2), ("B4", .5), ("D5", .5)], 0),
    ("was", "wuz", ["W", "AH", "Z"], [("B4", 2)], 0),
    ("lost", "lawst", ["L", "AO", "S", "T"], [("A4", 1), ("G4", 2)], 0),
    ("but", "butt", ["B", "AH", "T"], [("E4", 1)], 0),
    ("now", "now", ["N", "AW"], [("D4", 2)], 0),
    ("am", "am", ["AE", "M"], [("D4", 1)], 0),
    ("found", "fownd", ["F", "AW", "N", "D"], [("G4", 2), ("B4", .5), ("G4", .5)], 1),
    ("was", "wuz", ["W", "AH", "Z"], [("B4", 2)], 0),
    ("blind", "blynd", ["B", "L", "AY", "N", "D"], [("A4", 1)], 0),
    ("but", "butt", ["B", "AH", "T"], [("B4", 1)], 0),
    ("now", "now", ["N", "AW"], [("A4", 2)], 0),
    ("I", "eye", ["AY"], [("A4", 1)], 0),
    ("see", "see", ["S", "IY"], [("G4", 4.5)], 0),
]

# Formant targets (F1, F2, F3 in Hz) in the range of published adult female vowel averages.
VOWELS = {
    "AH": (760, 1400, 2780), "AA": (880, 1220, 2810), "AE": (860, 2050, 2850),
    "EH": (610, 2330, 2990), "IH": (430, 2480, 3070), "IY": (310, 2790, 3310),
    "UH": (470, 1160, 2680), "UW": (370, 950, 2670), "AO": (590, 920, 2710),
}
DIPHTHONGS = {"EY": ("EH", "IY"), "AY": ("AA", "IH"), "AW": ("AA", "UH")}
# phone: (F1, F2, F3, voice gain, noise gain, noise centre Hz, duration s, nasal)
CONSONANTS = {
    "M": (280, 1150, 2400, .85, 0, 0, .10, 1), "N": (280, 1650, 2700, .85, 0, 0, .10, 1),
    "NG": (280, 2300, 2750, .85, 0, 0, .11, 1), "L": (380, 1300, 3000, .62, 0, 0, .09, 0),
    "R": (470, 1250, 1750, .72, 0, 0, .09, 0), "W": (300, 720, 2400, .68, 0, 0, .09, 0),
    "Z": (300, 1700, 2700, .32, .13, 6000, .11, 0), "V": (300, 1100, 2500, .38, .04, 3500, .08, 0),
    "DH": (320, 1500, 2600, .42, .03, 3200, .07, 0), "S": (400, 1800, 2800, 0, .24, 6800, .14, 0),
    "F": (400, 1200, 2500, 0, .07, 4500, .13, 0), "HH": (600, 1500, 2700, 0, .12, 1800, .09, 0),
    "SH": (400, 2100, 2700, 0, .24, 3400, .11, 0),
    "B": (300, 1000, 2400, .1, 0, 0, .07, 0), "D": (300, 1700, 2700, .1, 0, 0, .07, 0),
    "G": (300, 2000, 2500, .1, 0, 0, .07, 0), "T": (350, 1800, 2800, 0, 0, 0, .08, 0),
    "K": (350, 2000, 2500, 0, 0, 0, .09, 0),
}
STOP_BURST = {"B": (.06, 1200), "D": (.09, 3800), "G": (.09, 2300), "T": (.17, 4800), "K": (.17, 2500)}
EXPAND = {"CH": ["T", "SH"]}
# Evens out the level differences that the narrow F1 resonance causes between vowels.
VOWEL_GAIN = {"AY": .5, "EH": .63, "IH": .75, "EY": 1.4, "IY": 1.45}


def phone_duration(p):
    return CONSONANTS[p][6]


def expand(phones):
    return [x for p in phones for x in EXPAND.get(p, [p])]


def is_vowel(p):
    return p in VOWELS or p in DIPHTHONGS


@numba.njit
def render(f0, av, f1, f2, f3, an, nc, nasal, sr, seed):
    np.random.seed(seed)
    n = len(f0)
    out = np.zeros(n)
    phase, period_jit, amp_jit = 0.0, 1.0, 1.0
    prev_g, tilt = 0.0, 0.0
    y = np.zeros((6, 2))
    ny = np.zeros(2)
    open_rise, open_fall = 0.40, 0.18
    for i in range(n):
        phase += f0[i] / sr * period_jit
        if phase >= 1.0:
            phase -= 1.0
            period_jit = 1.0 + 0.004 * np.random.normal()
            amp_jit = 1.0 + 0.02 * np.random.normal()
        if phase < open_rise:
            x = phase / open_rise
            g = 3 * x * x - 2 * x * x * x
        elif phase < open_rise + open_fall:
            x = (phase - open_rise) / open_fall
            g = 1 - x * x
        else:
            g = 0.0
        dg = (g - prev_g) * sr / 2000.0
        prev_g = g
        tilt += 0.55 * (dg - tilt)
        noise = np.random.normal()
        src = av[i] * amp_jit * tilt + 0.012 * av[i] * noise * (0.4 + g)

        freqs = (f1[i], f2[i], f3[i], 3900.0, 4800.0, 240.0)
        bands = (90.0 + 80 * nasal[i], 110.0, 170.0, 250.0, 320.0, 60.0)
        s = src
        for k in range(5):
            r = np.exp(-np.pi * bands[k] / sr)
            b, c = 2 * r * np.cos(2 * np.pi * freqs[k] / sr), -r * r
            v = (1 - b - c) * s + b * y[k, 0] + c * y[k, 1]
            y[k, 1], y[k, 0] = y[k, 0], v
            s = v
        if nasal[i] > 0.01:
            r = np.exp(-np.pi * 60.0 / sr)
            b, c = 2 * r * np.cos(2 * np.pi * 250.0 / sr), -r * r
            m = (1 - b - c) * src + b * y[5, 0] + c * y[5, 1]
            y[5, 1], y[5, 0] = y[5, 0], m
            s = s * (1 - 0.65 * nasal[i]) + 0.8 * nasal[i] * m

        r = np.exp(-np.pi * max(nc[i] * 0.45, 300.0) / sr)
        b, c = 2 * r * np.cos(2 * np.pi * max(nc[i], 300.0) / sr), -r * r
        v = (1 - b - c) * noise + b * ny[0] + c * ny[1]
        ny[1], ny[0] = ny[0], v
        out[i] = s + an[i] * 1.5 * v
    return out


def build_controls(rng):
    """Lay out the score in time and return control tracks at CTRL_SR plus the truth record."""
    beat = 60.0 / BPM
    lead_in = 1.0
    events, truth_notes, t = [], [], lead_in
    syllable_spans = []
    for grapheme, _, phones, notes, rest in SCORE:
        start = t
        for name, beats in notes:
            cents_err = float(rng.normal(0, 13))
            truth_notes.append({"start": t, "end": t + beats * beat, "midi": midi(name),
                                "cents_err": cents_err, "syllable": grapheme})
            events.append((t, t + beats * beat, midi(name) + cents_err / 100))
            t += beats * beat
        syllable_spans.append((grapheme, expand(phones), start, t, rest > 0))
        t += rest * beat
    end = t + 1.0
    n = int(end * CTRL_SR)

    # Consonants take time from the preceding vowel and from the end of their own note.
    segs = []
    for i, (g, phones, s, e, rested) in enumerate(syllable_spans):
        vi = next(k for k, p in enumerate(phones) if is_vowel(p))
        vowel_start, vowel_end = s, e - (0.06 if rested else 0.02)
        onset = phones[:vi]
        coda = phones[vi + 1:]
        cursor = s - sum(phone_duration(p) for p in onset)
        for p in onset:
            segs.append((p, cursor, cursor + phone_duration(p)))
            cursor += phone_duration(p)
        tail = sum(phone_duration(p) for p in coda)
        vowel_end -= tail
        segs.append((phones[vi], vowel_start, vowel_end))
        cursor = vowel_end
        for p in coda:
            segs.append((p, cursor, cursor + phone_duration(p)))
            cursor += phone_duration(p)

    f = np.zeros((3, n)) + np.array([[600.], [1500.], [2700.]])
    av, an, nc, nasal = np.zeros(n), np.zeros(n), np.full(n, 2000.0), np.zeros(n)
    for p, a, b in segs:
        ia, ib = int(a * CTRL_SR), max(int(b * CTRL_SR), int(a * CTRL_SR) + 1)
        ib = min(ib, n)
        if p in VOWELS or p in DIPHTHONGS:
            v0, v1 = DIPHTHONGS.get(p, (p, p))
            m = (ia + int((ib - ia) * (0.55 if v0 != v1 else 1.0)))
            for k in range(3):
                f[k, ia:ib] = VOWELS[v0][k]
                if v0 != v1:
                    f[k, m:ib] = np.linspace(VOWELS[v0][k], VOWELS[v1][k], ib - m)
            av[ia:ib] = VOWEL_GAIN.get(p, 1.0)
        else:
            c = CONSONANTS[p]
            for k in range(3):
                f[k, ia:ib] = c[k]
            av[ia:ib] = c[3]
            an[ia:ib] = c[4]
            nc[ia:ib] = c[5] if c[5] else 2000.0
            nasal[ia:ib] = c[7]
            if p in STOP_BURST:
                level, centre = STOP_BURST[p]
                an[max(ib - int(.022 * CTRL_SR), ia):ib] = level
                nc[max(ib - int(.022 * CTRL_SR), ia):ib] = centre

    # Open-vowel formant tuning: keep F1 above the sung fundamental on high notes.
    f0_midi = np.zeros(n)
    for s, e, m in events:
        f0_midi[int(s * CTRL_SR):int(e * CTRL_SR)] = m
    active = f0_midi > 0
    idx = np.where(active, np.arange(n), 0)
    idx = np.maximum.accumulate(idx)
    held = f0_midi[idx]
    first = int(np.argmax(active))
    held[:first] = f0_midi[first]
    # Glide between notes, then add scoops, vibrato and slow drift.
    smooth = ndi.gaussian_filter1d(held, 28 * CTRL_SR / 1000.0, mode="nearest")
    t_axis = np.arange(n) / CTRL_SR
    drift = ndi.gaussian_filter1d(rng.normal(0, 1, n), 120 * CTRL_SR / 1000.0)
    drift = drift / (np.std(drift) + 1e-9) * 0.07
    jitter_fast = ndi.gaussian_filter1d(rng.normal(0, 1, n), 12 * CTRL_SR / 1000.0)
    jitter_fast = jitter_fast / (np.std(jitter_fast) + 1e-9) * 0.025
    vib = np.zeros(n)
    for s, e, m in events:
        dur = e - s
        scoop_len = min(.12, dur * .3)
        ia, ib = int(s * CTRL_SR), int(e * CTRL_SR)
        sl = int(scoop_len * CTRL_SR)
        smooth[ia:ia + sl] -= 0.55 * np.linspace(1, 0, sl) ** 2
        if dur > 0.55:
            local = t_axis[ia:ib] - s
            rate = rng.uniform(5.0, 5.9)
            depth = rng.uniform(.28, .46)
            ramp = np.clip((local - .3) / .45, 0, 1)
            taper = np.clip((dur - local) / .08, 0, 1)
            vib[ia:ib] = depth * ramp * taper * np.sin(2 * np.pi * rate * local + rng.uniform(0, 6.28))
    pitch = smooth + drift + jitter_fast + vib
    f0 = 440.0 * 2 ** ((pitch - 69) / 12)
    f[0] = np.maximum(f[0], np.minimum(f0 * 1.08, 950.0))

    # Dynamics: a phrase arch, louder on high notes; onsets ramp in.
    phrase_gain = np.ones(n)
    level = ndi.gaussian_filter1d(pitch - pitch[active].mean(), 150 * CTRL_SR / 1000.0)
    phrase_gain *= 1.0 + 0.09 * level
    av *= phrase_gain

    rests = []
    spans = [(s, e) for _, _, s, e, _ in syllable_spans]
    for (a0, a1), (b0, _) in zip(spans, spans[1:]):
        if b0 - a1 > 0.3:
            rests.append((a1, b0))
    # Inhale noise in each rest, and before the first phrase.
    for a, b in [(lead_in - .75, lead_in - .1)] + [(a + .12, b - .12) for a, b in rests]:
        ia, ib = int(a * CTRL_SR), int(b * CTRL_SR)
        shape = np.sin(np.linspace(0, np.pi, ib - ia)) ** 1.5
        an[ia:ib] = np.maximum(an[ia:ib], 0.045 * shape)
        nc[ia:ib] = 1600.0

    win = 18
    av = ndi.gaussian_filter1d(av, win * CTRL_SR / 1000.0 / 2)
    an = ndi.gaussian_filter1d(an, 6 * CTRL_SR / 1000.0 / 2)
    nasal = ndi.gaussian_filter1d(nasal, 12)
    for k in range(3):
        f[k] = ndi.gaussian_filter1d(f[k], 16)

    truth = {
        "note": "Synthesizer ground truth. Read only by evaluate.py, never by analysis.",
        "bpm": BPM,
        "frame_hop_s": 1.0 / CTRL_SR,
        "notes": truth_notes,
        "f0_midi_voiced": [round(float(x), 3) if v > 0.2 else None
                           for x, v in zip(pitch[::10], av[::10])],
        "phones": [{"phone": p, "start": round(a, 3), "end": round(b, 3)} for p, a, b in segs],
    }
    return f0, av, f[0], f[1], f[2], an, nc, nasal, truth


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="assets/demo_audio/amazing_grace_synth.wav")
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    f0, av, f1, f2, f3, an, nc, nasal, truth = build_controls(rng)
    n = int(len(f0) * SR / CTRL_SR)
    xs = np.arange(n) / SR * CTRL_SR
    grid = np.arange(len(f0))
    tracks = [np.interp(xs, grid, x) for x in (f0, av, f1, f2, f3, an, nc, nasal)]
    y = render(*tracks, SR, args.seed)
    y = sig.decimate(y, OVERSAMPLE, ftype="fir", zero_phase=True)
    # A short diffuse tail keeps the voice from sounding bone dry.
    tail_rng = np.random.default_rng(args.seed + 1)
    tl = int(.22 * SR_OUT)
    tail = tail_rng.normal(0, 1, tl) * np.exp(-np.arange(tl) / (.06 * SR_OUT))
    tail = tail / np.sqrt(np.sum(tail ** 2))
    y = y + .16 * sig.fftconvolve(y, tail)[:len(y)]
    y = sig.sosfiltfilt(sig.butter(2, 90 / (SR_OUT / 2), "highpass", output="sos"), y)
    y = y / np.max(np.abs(y)) * 0.8

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out, y, SR_OUT, subtype="PCM_16")
    lyrics = {"title": "Amazing Grace (traditional)",
              "subtitle": "AMAZING GRACE · SYNTHESIZED DEMO VOICE",
              "syllables": [{"grapheme": g, "pron": p, "phones": ph, "notes": len(ns)}
                            for g, p, ph, ns, _ in SCORE]}
    stem = out.with_suffix("")
    stem.with_suffix(".lyrics.json").write_text(json.dumps(lyrics, indent=1))
    stem.with_suffix(".truth.json").write_text(json.dumps(truth))
    print(f"wrote {out} ({len(y) / SR_OUT:.1f}s)")


if __name__ == "__main__":
    main()
