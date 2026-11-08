#!/usr/bin/env python3
"""Turn a singing clip into the data file that drives the dashboard.

Extracted from the audio: pitch (pYIN), voicing, energy, note segments, breath gaps.
Given as text, optionally: lyric syllables and phones, aligned here to the detected notes.
Illustrative, derived by rule: articulator positions, airflow and lung volume.
"""
import argparse
import json
from pathlib import Path

import librosa
import numpy as np
import scipy.ndimage as ndi

ANALYSIS_SR = 22050
HOP = 256
FPS = 100
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Illustrative articulator targets, 0..1:
# tongue height, tongue backness, tongue tip, jaw opening, lip rounding, velum opening
AH, AA = (.42, .5, .1, .65, .05, 0), (.15, .75, .08, .9, .05, 0)
AE, EH = (.3, .15, .12, .8, 0, 0), (.55, .2, .15, .55, 0, 0)
IH, IY = (.78, .15, .2, .3, 0, 0), (.95, .1, .25, .15, .02, 0)
UH, UW = (.72, .85, .08, .3, .55, 0), (.9, .95, .05, .18, .9, 0)
AO = (.3, .9, .05, .6, .65, 0)
TARGETS = {
    "AH": AH, "AA": AA, "AE": AE, "EH": EH, "IH": IH, "IY": IY, "UH": UH, "UW": UW, "AO": AO,
    "M": (.4, .4, .1, .05, .25, 1), "N": (.6, .3, .95, .15, 0, 1), "NG": (.85, .9, .05, .2, 0, 1),
    "L": (.55, .35, .9, .3, 0, 0), "R": (.6, .6, .55, .3, .3, 0), "W": (.8, .95, .05, .2, .95, 0),
    "S": (.75, .2, .85, .12, 0, 0), "Z": (.75, .2, .85, .12, 0, 0),
    "SH": (.75, .3, .6, .15, .35, 0), "CH": (.78, .28, .8, .12, .3, 0),
    "F": (.45, .4, .15, .12, .1, 0), "V": (.45, .4, .15, .12, .1, 0),
    "DH": (.55, .25, .8, .2, 0, 0), "T": (.72, .25, 1, .12, 0, 0), "D": (.72, .25, 1, .12, 0, 0),
    "K": (.95, .9, .05, .22, 0, 0), "G": (.95, .9, .05, .22, 0, 0),
    "B": (.4, .4, .1, .03, .3, 0), "HH": (.4, .5, .1, .5, 0, 0),
}
DIPHTHONGS = {"EY": (EH, IY), "AY": (AA, IH), "AW": (AA, UH)}
REST = (.35, .5, .1, .12, .05, 1)
# How much of the phone's airflow escapes (illustrative): 0 for stop closure, 1 for open vowels.
OPENNESS = {"M": .5, "N": .5, "NG": .5, "L": .75, "R": .85, "W": .75, "S": .7, "Z": .65,
            "SH": .7, "CH": .55, "F": .55, "V": .5, "DH": .55, "T": .08, "D": .08, "K": .08,
            "G": .08, "B": .08, "HH": .8}
CONSONANT_S = {"S": .13, "Z": .1, "F": .12, "V": .08, "DH": .07, "M": .09, "N": .09, "NG": .1,
               "L": .09, "R": .09, "W": .09, "SH": .11, "CH": .12, "T": .07, "D": .07, "K": .08,
               "G": .07, "B": .07, "HH": .09}
IPA = {"AH": "ʌ", "AA": "ɑ", "AE": "æ", "EH": "ɛ", "IH": "ɪ", "IY": "i", "UH": "ʊ", "UW": "u",
       "AO": "ɔ", "EY": "eɪ", "AY": "aɪ", "AW": "aʊ", "M": "m", "N": "n", "NG": "ŋ", "L": "l",
       "R": "ɹ", "W": "w", "S": "s", "Z": "z", "SH": "ʃ", "CH": "tʃ", "F": "f", "V": "v",
       "DH": "ð", "T": "t", "D": "d", "K": "k", "G": "g", "B": "b", "HH": "h"}
# Vowel centres (F1, F2) used only when no lyrics are given.
FORMANT_VOWELS = {"IY": (310, 2790), "IH": (430, 2480), "EH": (610, 2330), "AE": (860, 2050),
                  "AA": (880, 1220), "AH": (760, 1400), "AO": (590, 920), "UH": (470, 1160),
                  "UW": (370, 950)}


def is_vowel(p):
    return p in DIPHTHONGS or p in FORMANT_VOWELS


def note_name(m):
    m = int(round(m))
    return f"{NAMES[m % 12]}{m // 12 - 1}"


def fix_note_octaves(notes, t, midi):
    """Fold a whole note onto the octave that fits its neighbouring notes."""
    medians = [n["median"] for n in notes]
    for i, n in enumerate(notes):
        around = medians[max(0, i - 4):i] + medians[i + 1:i + 5]
        if not around:
            continue
        centre = np.median(around)
        k = np.round((centre - n["median"]) / 12)
        if k != 0 and abs(n["median"] + 12 * k - centre) < abs(n["median"] - centre) - 6:
            mask = (t >= n["start"]) & (t < n["end"]) & np.isfinite(midi)
            midi[mask] += 12 * k
            n["median"] += 12 * k
            n["midi"] = int(np.round(n["median"]))


def extract_pitch(y):
    f0, voiced, prob = librosa.pyin(y, fmin=librosa.note_to_hz("C3"), fmax=librosa.note_to_hz("A5"),
                                    sr=ANALYSIS_SR, frame_length=2048, hop_length=HOP)
    t = librosa.times_like(f0, sr=ANALYSIS_SR, hop_length=HOP)
    midi = 69 + 12 * np.log2(np.where(voiced, f0, np.nan) / 440.0)
    return t, fix_octaves(midi, t[1] - t[0]), np.asarray(voiced, bool), prob


def fix_octaves(midi, hop):
    """Fold frames that sit about an octave away from the local median back onto it."""
    out = midi.copy()
    half = int(.4 / hop)
    for i in np.where(np.isfinite(midi))[0]:
        around = midi[max(0, i - half):i + half]
        around = around[np.isfinite(around)]
        k = np.round((np.median(around) - midi[i]) / 12)
        if k != 0 and abs(midi[i] + 12 * k - np.median(around)) < 2.5:
            out[i] = midi[i] + 12 * k
    return out


def segment_notes(t, midi, energy):
    """Split voiced runs at sustained pitch changes and at dips in energy."""
    hop = t[1] - t[0]
    voiced = np.isfinite(midi)
    filled = np.where(voiced, midi, 0.0)
    med = ndi.median_filter(filled, size=max(3, int(.07 / hop) | 1))
    labels, count = ndi.label(voiced)
    runs = [(s[0].start, s[0].stop) for s in ndi.find_objects(labels)]

    # Bridge very short unvoiced gaps, which are consonants inside a held line.
    merged = []
    for s, e in runs:
        if merged and (s - merged[-1][1]) * hop < 0.05:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))

    notes = []
    min_len = int(.09 / hop)
    settle = int(.08 / hop)
    for s, e in merged:
        cuts = [s]
        cur = med[s + min(settle, (e - s) // 2)]
        i = s + settle
        while i < e - settle:
            if abs(med[i] - cur) > 0.65:
                window = med[i:i + settle]
                if np.all(np.abs(window - window[0]) < 0.6) and abs(window.mean() - cur) > 0.65:
                    j = i
                    while j > cuts[-1] + 1 and abs(med[j] - cur) > 0.3:
                        j -= 1
                    cuts.append(j)
                    cur = window.mean()
                    i += settle
                    continue
            cur = 0.97 * cur + 0.03 * med[i]
            i += 1
        cuts.append(e)
        # Repeated pitches are separated by the consonant's dip in level.
        final = []
        for a, b in zip(cuts, cuts[1:]):
            final.append(a)
            if (b - a) * hop > .6:
                seg = energy[a:b]
                smooth = ndi.gaussian_filter1d(seg, .012 / hop)
                k = int(np.argmin(smooth[int(.25 / hop):-int(.25 / hop)])) + int(.25 / hop)
                if smooth[k] < 0.5 * min(smooth[:k].max(), smooth[k:].max()):
                    final.append(a + k)
        final.append(e)
        for a, b in zip(final, final[1:]):
            if b - a < min_len:
                continue
            core = med[a + (b - a) // 5:b - (b - a) // 5]
            core = core[core > 0]
            if len(core):
                notes.append({"start": float(t[a]), "end": float(t[min(b, len(t) - 1)]),
                              "midi": int(np.round(np.median(core))), "median": float(np.median(core))})
    return drop_glides(notes)


def drop_glides(notes):
    """Remove short notes that are only the slide between two neighbouring notes."""
    kept = []
    for i, n in enumerate(notes):
        if 0 < i < len(notes) - 1 and n["end"] - n["start"] < .18:
            a, b = notes[i - 1], notes[i + 1]
            touching = n["start"] - a["end"] < .03 and b["start"] - n["end"] < .03
            if touching and min(a["median"], b["median"]) < n["median"] < max(a["median"], b["median"]):
                b["start"] = n["start"]
                continue
        kept.append(n)
    return kept


def nearest_vowel(y, sr, a, b):
    """Coarse LPC vowel guess for no-lyrics runs. Unreliable at high pitch."""
    frame = y[int(a * sr):int(b * sr)]
    if len(frame) < 1024:
        return "AH"
    frame = frame[:4096] * np.hanning(min(4096, len(frame)))
    roots = np.roots(librosa.lpc(frame, order=12))
    roots = roots[np.imag(roots) > 0]
    freqs = sorted(np.angle(roots) * sr / (2 * np.pi))
    freqs = [f for f in freqs if 200 < f < 3500]
    if len(freqs) < 2:
        return "AH"
    f1, f2 = freqs[0], freqs[1]
    return min(FORMANT_VOWELS, key=lambda p: ((FORMANT_VOWELS[p][0] - f1) / 200) ** 2 +
               ((FORMANT_VOWELS[p][1] - f2) / 500) ** 2)


def align_lyrics(notes, lyrics):
    """Assign syllables to detected notes in order, using each syllable's note count."""
    syllables = lyrics["syllables"]
    expected = sum(s.get("notes", 1) for s in syllables)
    warning = None
    if expected != len(notes):
        warning = (f"expected {expected} notes from the lyrics, detected {len(notes)}: "
                   "syllables spread proportionally, timing is approximate")
    out, cursor = [], 0
    for i, s in enumerate(syllables):
        want = s.get("notes", 1)
        if warning:
            first = round(i * len(notes) / len(syllables))
            last = round((i + 1) * len(notes) / len(syllables))
        else:
            first, last = cursor, cursor + want
        cursor += want
        group = notes[first:max(last, first + 1)]
        if group:
            out.append({"grapheme": s["grapheme"], "pron": s["pron"], "phones": s["phones"],
                        "first_note": first, "last_note": first + len(group) - 1,
                        "start": group[0]["start"], "end": group[-1]["end"]})
    return out, warning


def place_phones(syllables, duration):
    """Spread each syllable's phones: onset before the note, coda inside its end."""
    spans = []
    prev_end = 0.0
    for s in syllables:
        phones = s["phones"]
        vowel = next((k for k, p in enumerate(phones) if is_vowel(p)), 0)
        onset, coda = phones[:vowel], phones[vowel + 1:]
        coda_total = sum(CONSONANT_S.get(p, .08) for p in coda)
        coda_total = min(coda_total, .45 * (s["end"] - s["start"]))
        onset_room = min(sum(CONSONANT_S.get(p, .08) for p in onset), max(0.0, s["start"] - prev_end))
        cursor = s["start"] - onset_room
        scale = onset_room / max(1e-6, sum(CONSONANT_S.get(p, .08) for p in onset))
        for p in onset:
            d = CONSONANT_S.get(p, .08) * scale
            spans.append({"phone": p, "start": cursor, "end": cursor + d, "vowel": False})
            cursor += d
        vowel_end = s["end"] - coda_total
        spans.append({"phone": phones[vowel], "start": s["start"], "end": vowel_end, "vowel": True})
        cursor = vowel_end
        unit = coda_total / max(1e-6, sum(CONSONANT_S.get(p, .08) for p in coda))
        for p in coda:
            d = CONSONANT_S.get(p, .08) * unit
            spans.append({"phone": p, "start": cursor, "end": min(cursor + d, duration), "vowel": False})
            cursor += d
        prev_end = s["end"]
    for span in spans:
        span["ipa"] = IPA.get(span["phone"], span["phone"].lower())
    return spans


def track_to_grid(t, values, grid):
    return np.interp(grid, t, values, left=values[0], right=values[-1])


def illustrative_tracks(grid, phones, voice, energy, midi):
    """Rule-based articulation, airflow and lung volume. None of this is measured."""
    n = len(grid)
    arts = np.tile(np.array(REST, float), (n, 1))
    open_track = np.zeros(n)
    active = np.zeros(n, bool)
    for p in phones:
        ia, ib = np.searchsorted(grid, [p["start"], p["end"]])
        if ib <= ia:
            continue
        name = p["phone"]
        active[ia:ib] = True
        open_track[ia:ib] = OPENNESS.get(name, 1.0)
        if name in DIPHTHONGS:
            a, b = (np.array(x, float) for x in DIPHTHONGS[name])
            k = np.clip((np.arange(ia, ib) - ia) / max(1, ib - ia - 1) - .35, 0, 1) / .65
            arts[ia:ib] = a[None] * (1 - k[:, None]) + b[None] * k[:, None]
        else:
            arts[ia:ib] = TARGETS.get(name, REST)

    # Double smoothing stands in for coarticulation.
    for _ in range(2):
        arts = ndi.gaussian_filter1d(arts, 2.2, axis=0, mode="nearest")
    open_track = ndi.gaussian_filter1d(open_track, 2.2, mode="nearest")

    # Illustrative only: singers often open the jaw wider on higher notes.
    filled = np.where(np.isfinite(midi), midi, np.nan)
    pitch_lift = np.nan_to_num(np.clip((filled - 62) / 12, 0, 1)) * 0.22
    arts[:, 3] = np.clip(arts[:, 3] + pitch_lift * (arts[:, 3] > .25), 0, 1)

    airflow = np.clip(energy * (0.15 + 0.85 * open_track) * (0.3 + 0.7 * voice), 0, 1)
    return arts, airflow


def lung_and_breath(grid, voice_mask, energy):
    """Inhale in each pause; spend breath in proportion to loudness. Illustrative."""
    n = len(grid)
    dt = grid[1] - grid[0]
    labels, count = ndi.label(voice_mask)
    voiced_runs = [(s[0].start, s[0].stop) for s in ndi.find_objects(labels)]
    phrases = []
    for a, b in voiced_runs:
        if phrases and (a - phrases[-1][1]) * dt < 0.28:
            phrases[-1] = (phrases[-1][0], b)
        else:
            phrases.append((a, b))
    lung, inhale = np.full(n, .3), np.zeros(n)
    prev_end, level = 0, .34
    breaths = []
    for a, b in phrases:
        if a > prev_end:
            k = np.linspace(0, 1, a - prev_end)
            ease = k * k * (3 - 2 * k)
            lung[prev_end:a] = level + (.9 - level) * ease
            inhale[prev_end:a] = np.sin(np.pi * k) ** 1.5
            breaths.append({"start": float(grid[prev_end]), "end": float(grid[a - 1])})
        spent = np.cumsum(np.maximum(energy[a:b], .05))
        spent = spent / spent[-1]
        lung[a:b] = .9 - .6 * spent
        level = lung[b - 1]
        prev_end = b
    if prev_end < n:
        k = np.linspace(0, 1, n - prev_end)
        lung[prev_end:] = level + (.5 - level) * k
    return lung, inhale, breaths


def analyze(audio_path, lyrics_path):
    y, _ = librosa.load(audio_path, sr=ANALYSIS_SR, mono=True)
    y = y / (np.max(np.abs(y)) + 1e-9)
    duration = len(y) / ANALYSIS_SR
    t, midi, _, prob = extract_pitch(y)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=HOP)[0]
    rms = rms[:len(t)]
    energy = np.clip(rms / np.percentile(rms[rms > 1e-5], 98), 0, 1)
    notes = segment_notes(t, midi, energy)
    fix_note_octaves(notes, t, midi)

    grid = np.arange(0, duration, 1.0 / FPS)
    # Nearest frame, not interpolation: blending voiced with unvoiced frames invents pitches.
    nearest = np.clip(np.round(grid / (t[1] - t[0])).astype(int), 0, len(t) - 1)
    midi_grid = midi[nearest]
    voiced_grid = np.isfinite(midi_grid)
    energy_grid = track_to_grid(t, energy, grid)
    energy_grid = np.clip(ndi.gaussian_filter1d(energy_grid, 1.0), 0, 1)

    lyrics = None
    warning = None
    if lyrics_path and Path(lyrics_path).exists():
        lyrics = json.loads(Path(lyrics_path).read_text())
        syllables, warning = align_lyrics(notes, lyrics)
    else:
        syllables = []
        for i, note in enumerate(notes):
            vowel = nearest_vowel(y, ANALYSIS_SR, note["start"], note["end"])
            syllables.append({"grapheme": IPA[vowel], "pron": note_name(note["midi"]).lower(),
                              "phones": [vowel], "first_note": i, "last_note": i,
                              "start": note["start"], "end": note["end"]})
    phones = place_phones(syllables, duration)

    voice_mask = voiced_grid | (energy_grid > .04)
    # Fill short consonant gaps so that a sung line is not read as a pause.
    voice_mask = ndi.binary_closing(voice_mask, np.ones(int(.28 * FPS)))
    lung, inhale, breaths = lung_and_breath(grid, voice_mask, energy_grid)
    arts, airflow = illustrative_tracks(grid, phones, voiced_grid.astype(float), energy_grid, midi_grid)
    airflow = np.maximum(airflow, 0.0)

    note_of = -np.ones(len(grid), int)
    for i, note in enumerate(notes):
        note_of[(grid >= note["start"]) & (grid < note["end"])] = i
    deviation = np.full(len(grid), np.nan)
    for i, note in enumerate(notes):
        mask = note_of == i
        deviation[mask] = (midi_grid[mask] - note["midi"]) * 100

    out = {
        "meta": {
            "title": lyrics["title"] if lyrics else Path(audio_path).stem,
            "subtitle": lyrics["subtitle"] if lyrics else Path(audio_path).stem.upper(),
            "duration": duration, "fps": FPS, "source": Path(audio_path).name,
            "pitch_method": "librosa pYIN, 22.05 kHz, 2048/256 frame/hop, C3-A5",
            "phones_from": "lyric text aligned to detected notes" if lyrics else "LPC vowel estimate",
            "alignment_warning": warning,
        },
        "notes": [{"start": round(n["start"], 3), "end": round(n["end"], 3), "midi": n["midi"],
                   "name": note_name(n["midi"])} for n in notes],
        "syllables": syllables,
        "phones": phones,
        "breaths": breaths,
        "tracks": {
            "midi": [None if not np.isfinite(m) else round(float(m), 3) for m in midi_grid],
            "deviation": [None if not np.isfinite(d) else round(float(d), 1) for d in deviation],
            "energy": np.round(energy_grid, 3).tolist(),
            "inhale": np.round(inhale, 3).tolist(),
            "lung": np.round(lung, 3).tolist(),
            "airflow": np.round(airflow, 3).tolist(),
            "voiced": voiced_grid.astype(int).tolist(),
            "tongue_height": np.round(arts[:, 0], 3).tolist(),
            "tongue_back": np.round(arts[:, 1], 3).tolist(),
            "tongue_tip": np.round(arts[:, 2], 3).tolist(),
            "jaw": np.round(arts[:, 3], 3).tolist(),
            "lips": np.round(arts[:, 4], 3).tolist(),
            "velum": np.round(arts[:, 5], 3).tolist(),
        },
    }
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("audio")
    ap.add_argument("--lyrics", help="syllable JSON; if omitted, vowels are estimated by LPC")
    ap.add_argument("--out", default="results/analysis.json")
    args = ap.parse_args()
    data = analyze(args.audio, args.lyrics)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data))
    m = data["meta"]
    print(f"{len(data['notes'])} notes, {len(data['syllables'])} syllables, "
          f"{len(data['breaths'])} breaths, {m['duration']:.1f}s")
    if m["alignment_warning"]:
        print("WARNING:", m["alignment_warning"])


if __name__ == "__main__":
    main()
