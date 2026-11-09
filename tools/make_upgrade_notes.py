#!/usr/bin/env python3
"""Performance planner for the voice upgrade: turns the sealed Amazing Grace score into CHIMERA notes plus gestures.

Adds what the score alone lacks: a voice profile, inhales through the airway, pressure shaped over each phrase,
per-note vibrato and pitch approach. No audio involved. Usage: make_upgrade_notes.py --stage A --out <stem>
"""
import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/demo_audio/amazing_grace_chimera"
SEED = 29
SOURCES = {
    "A": {"tension": .46, "brightness": .16, "vibratoRate": 6.1},
    "B": {"tension": .46, "brightness": .16, "vibratoRate": 6.1},
    "C": {"tension": .46, "brightness": .16, "vibratoRate": 6.1},
}
# Stage C: one fictional body, a tract between the adult female and male presets. Models no real person.
BODY_MIX = {"female": .85, "child": 0}
Z_ABDUCTION = .07
PRIOR_SEGMENTS = ROOT / "assets/demo_audio/amazing_grace_upgrade_r1.segments.json"
TENSION_PER_SEMITONE = .025
FRICATIVE_SCALE = .75
INHALE_PRESSURE, INHALE_ABDUCTION = .3, .25
INHALE_RAMP, INHALE_CLEAR = .1, .02
INHALE_MIN_SPAN = .08  # the earlier end shortens the span; a rest of .5 s must still get its inhale


def gesture(t0, t1, ramp_in, ramp_out, strength, label, **targets):
    return {"t0": round(t0, 4), "t1": round(t1, 4), "rampIn": ramp_in, "rampOut": ramp_out, "strength": strength, "targets": targets, "label": label}


def layout(j):
    """Sounding notes grouped into phrases, with their times in seconds."""
    beat = 60 / j["bpm"]
    t, phrases, cur = j["t0"], [], []
    for midi, beats in j["notes"]:
        if midi > 0:
            cur.append({"midi": midi, "start": t, "end": t + beats * beat})
        elif cur:
            phrases.append(cur)
            cur = []
        t += beats * beat
    if cur:
        phrases.append(cur)
    return phrases


def pressure(phrase, mean_midi):
    """Breath pressure over a phrase: an arc, louder high notes, swells on long notes, a decay at the end."""
    out = []
    a, b = phrase[0]["start"], phrase[-1]["end"]
    for i, n in enumerate(phrase):
        d = n["end"] - n["start"]
        centre = (n["start"] + n["end"]) / 2
        v = .94 + .12 * np.sin(np.pi * (centre - a) / (b - a)) + .012 * (n["midi"] - mean_midi)
        if i == len(phrase) - 1:
            parts = [(0, .5, 1.0), (.5, 1, .68)]
        elif d >= .9:
            parts = [(0, .35, .95), (.35, .75, 1.05), (.75, 1, .97)]
        else:
            parts = [(0, 1, 1.0)]
        for p, q, k in parts:
            out.append(gesture(n["start"] + p * d - .02, n["start"] + q * d, .05, .05, 8.0, "phrase", breath=round(float(v * k), 3)))
    return out


def first_onsets(phrases, segments):
    """Start of each phrase's first scheduled segment, onset consonants included, from the engine's plan."""
    t = [s["t0"] for s in segments]
    return [t[0]] + [next(x for x in t if x >= a[-1]["end"]) for a in phrases[:-1]]


def inhales(phrases, t0, onsets=None):
    """Inhales in the rests. With `onsets` (see first_onsets) each one, ramp included, ends INHALE_CLEAR before the phrase's first consonant."""
    ends = [o - INHALE_RAMP - INHALE_CLEAR for o in onsets] if onsets else [p[0]["start"] - .14 for p in phrases]
    if not onsets:
        ends[0] = t0 - .14
    spans = [(.22, ends[0])]
    spans += [(a[-1]["end"] + .16, q) for a, q in zip(phrases, ends[1:])]
    return [gesture(p, q, .1, .1, 8.0, "inhale", breath=-INHALE_PRESSURE, abduction=INHALE_ABDUCTION) for p, q in spans if q - p > (INHALE_MIN_SPAN if onsets else .2)]


def tension(phrases, mean_midi):
    """Laxer folds on low notes, firmer on high ones, so the first harmonic falls against the second as pitch rises."""
    base = SOURCES["B"]["tension"]
    return [gesture(n["start"] - .03, n["end"], .06, .06, 8.0, "tension", tension=round(float(np.clip(base + TENSION_PER_SEMITONE * (n["midi"] - mean_midi), .2, .75)), 3))
            for p in phrases for n in p]


def vibrato(phrases, rng, per_note_rate=False):
    """About two thirds of the long notes, with depth and bloom varied; a phrase's held last note always gets it."""
    out = []
    for ph in phrases:
        for i, n in enumerate(ph):
            d = n["end"] - n["start"]
            last = i == len(ph) - 1 and d >= 1.4
            if d < .7 or not (last or rng.random() < .62):
                continue
            depth = float(rng.uniform(40, 50) if last else rng.uniform(26, 44))
            bloom = float(rng.uniform(.2, .35))
            out.append(gesture(n["start"] + bloom, n["end"] - .05, .3, .06, 4.0, "vibrato", vibrato=round(depth, 1)))
            if per_note_rate:
                out.append(gesture(n["start"], n["end"], .05, .05, 4.0, "vibrato rate", vibratoRate=round(float(rng.uniform(5.7, 6.5)), 2)))
    return out


def approaches(phrases):
    out = []
    for ph in phrases:
        for a, b in zip(ph, ph[1:]):
            if b["midi"] - a["midi"] >= 2:
                hz = 440 * 2 ** ((b["midi"] - 69) / 12) * 2 ** (-40 / 1200)
                out.append(gesture(b["start"] - .02, b["start"] + .06, .02, .03, 30.0, "pitch", f0=round(hz, 3)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", default="A", choices=sorted(SOURCES))
    ap.add_argument("--out", required=True)
    ap.add_argument("--rules", action="store_true", help="turn on the engine's phonology rules")
    ap.add_argument("--plan", help="segments JSON of a --plan-only engine pass: times inhales and /z/ from this plan")
    args = ap.parse_args()
    j = json.loads(SRC.with_suffix(".notes.json").read_text())
    plan = json.loads(Path(args.plan).read_text()) if args.plan else None
    rng = np.random.default_rng(SEED)
    phrases = layout(j)
    mean_midi = float(np.mean([n["midi"] for p in phrases for n in p]))
    gestures = [g for p in phrases for g in pressure(p, mean_midi)] + inhales(phrases, j["t0"], first_onsets(phrases, plan) if plan else None) + vibrato(phrases, rng, args.stage != "A") + approaches(phrases)
    if args.stage != "A":
        gestures += tension(phrases, mean_midi)
    if args.stage == "C":
        # A wider glottis during /z/ gives the jet more flow, so it has frication under its voicing.
        gestures += [gesture(s["t0"] - .01, s["t1"], .02, .02, 8.0, "z", abduction=Z_ABDUCTION) for s in (plan or json.loads(PRIOR_SEGMENTS.read_text())) if s["ipa"] == "z"]
        j["bodyMix"] = BODY_MIX
    j.update(source=SOURCES[args.stage], fricativeScale=FRICATIVE_SCALE, externalVibrato=True, gestures=gestures)
    if args.rules:
        j["phonologyRules"] = True
    out = Path(args.out)
    out.with_suffix(".notes.json").write_text(json.dumps(j, indent=1) + "\n")
    lyrics = json.loads(SRC.with_suffix(".lyrics.json").read_text())
    lyrics["subtitle"] = f"AMAZING GRACE · VOICE UPGRADE (CHIMERA PATCH, STAGE {args.stage})"
    out.with_suffix(".lyrics.json").write_text(json.dumps(lyrics, indent=1) + "\n")
    print(f"{out.name}: {len(gestures)} gestures in {len(phrases)} phrases")


if __name__ == "__main__":
    main()
