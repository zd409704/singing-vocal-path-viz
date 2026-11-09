"""Scores for the comparative page: the shared planner's two-pass output for the songs, and short probes.

Score settings (song, planner seed, transposition, tempo) are separate from model settings. At seed 29 with no
transposition or tempo change a song matches the `*_algo.notes.json` planner output. Reads only; writes where told.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import make_nursery_notes as nursery  # noqa: E402
import make_upgrade_notes as upgrade  # noqa: E402
import paths  # noqa: E402

# Plan pass stays on the upgraded-algo checkpoint. mech-c3 and upstream are different engines.
SONGS = ["twinkle", "two_tigers", "amazing_grace", "probe_vowel", "probe_sweep", "probe_consonant"]
DEFAULT = {"song": "twinkle", "seed": 29, "transpose": 0, "tempo": 1.0}
PROBE_LEXICON = {"pa": "P AA1", "ta": "T AA1", "ka": "K AA1", "sa": "S AA1", "sha": "SH AA1", "fa": "F AA1", "ma": "M AA1", "na": "N AA1", "la": "L AA1", "ra": "R AA1", "za": "Z AA1", "ga": "G AA1"}
PROBES = {
    "probe_vowel": {"bpm": 60, "lyrics": "ah", "notes": [[64, 4.0]], "title": "Sustained vowel /a/, E4, 4 s"},
    "probe_sweep": {"bpm": 120, "lyrics": " ".join(["ah"] * 39), "notes": [[m, 1.0] for m in list(range(57, 77)) + list(range(75, 56, -1))], "title": "Chromatic sweep A3 to E5 and back on /a/"},
    "probe_consonant": {"bpm": 72, "lyrics": "pa ta ka sa sha fa ma na la ra za ga", "notes": [[64, 1.0]] * 12, "title": "Consonants before /a/ on E4"},
}


def _gestures(j, seed, plan, song):
    rng = np.random.default_rng(seed)
    phrases = upgrade.layout(j)
    mean_midi = float(np.mean([n["midi"] for p in phrases for n in p]))
    onsets = upgrade.first_onsets(phrases, plan) if plan else None
    if song == "amazing_grace":
        gs = [g for p in phrases for g in upgrade.pressure(p, mean_midi)] + upgrade.inhales(phrases, j["t0"], onsets) + upgrade.vibrato(phrases, rng, True) + upgrade.approaches(phrases)
        gs += upgrade.tension(phrases, mean_midi)
        segs = plan or json.loads(upgrade.PRIOR_SEGMENTS.read_text())
        gs += [upgrade.gesture(s["t0"] - .01, s["t1"], .02, .02, 8.0, "z", abduction=upgrade.Z_ABDUCTION) for s in segs if s["ipa"] == "z"]
    else:
        gs = [g for p in phrases for g in upgrade.pressure(p, mean_midi)] + upgrade.inhales(phrases, j["t0"], onsets) + upgrade.vibrato(phrases, rng, True) + upgrade.approaches(phrases) + upgrade.tension(phrases, mean_midi)
    return gs


def _base(song, transpose, tempo):
    if song == "amazing_grace":
        j = json.loads(upgrade.SRC.with_suffix(".notes.json").read_text())
    elif song in PROBES:
        p = PROBES[song]
        j = {"bpm": p["bpm"], "t0": 1.0, "vibrato": 35, "lyrics": p["lyrics"], "notes": [list(n) for n in p["notes"]], "lexicon": PROBE_LEXICON}
    else:
        s = {"twinkle": nursery.twinkle, "two_tigers": nursery.two_tigers}[song]()
        lexicon = nursery.pinyin_lexicon(s["rows"]) if s.get("pinyin") else {}
        if lexicon:
            tok = {x: (x if x in lexicon else nursery.PINYIN[x][0]) for x in nursery.PINYIN}
            s["lyrics"] = " ".join(tok[x] for _, ss in s["rows"] for x in ss)
        j = {"bpm": s["bpm"], "t0": 1.0, "vibrato": 35, "lyrics": s["lyrics"], "notes": [list(n) for row, _ in s["rows"] for n in row]}
        if lexicon:
            j["lexicon"] = {w: nursery.stressed(p) for w, p in lexicon.items()}
    j["notes"] = [[(n[0] + transpose if n[0] > 0 else n[0]), n[1]] for n in j["notes"]]
    j["bpm"] = j["bpm"] * tempo
    return j


def _finish(j, song, gestures):
    lex = j.pop("lexicon", None)
    j["bodyMix"] = upgrade.BODY_MIX
    j.update(source=upgrade.SOURCES["C"], fricativeScale=upgrade.FRICATIVE_SCALE, externalVibrato=True, gestures=gestures, phonologyRules=True)
    if lex:
        j["lexicon"] = lex
    return j


def build(score, workdir):
    """The notes JSON for a score, using the pinned upgraded engine for the plan pass."""
    s = {**DEFAULT, **score}
    if s["song"] not in SONGS:
        raise ValueError(f"unknown song {s['song']!r}")
    transpose, tempo, seed = int(s["transpose"]), float(s["tempo"]), int(s["seed"])
    if not -12 <= transpose <= 12 or not 0.5 <= tempo <= 2.0:
        raise ValueError("transpose must be -12..12 and tempo 0.5..2")
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    first = _finish(_base(s["song"], transpose, tempo), s["song"], [])
    first["gestures"] = _gestures(first, seed, None, s["song"])
    p1, seg = workdir / "pass1.notes.json", workdir / "pass1.segments.json"
    p1.write_text(json.dumps(first))
    plan_bin = paths.engine_binary("upgraded-algo")
    subprocess.run([str(plan_bin), "render", "notes", str(p1), str(workdir / "plan"), "female", "--plan-only", "--segments", str(seg)], check=True, capture_output=True, text=True)
    final = _finish(_base(s["song"], transpose, tempo), s["song"], [])
    final["gestures"] = _gestures(final, seed, json.loads(seg.read_text()), s["song"])
    return final


def score_key(score):
    return hashlib.sha256(json.dumps({**DEFAULT, **score}, sort_keys=True).encode()).hexdigest()[:16]
