#!/usr/bin/env python3
"""Performance planner for the two public-domain nursery rhymes: scores written here, gestures from the Stage C planner.

One lyric syllable per sounding note. No audio involved. Usage: make_nursery_notes.py <twinkle|two_tigers> --out <stem>
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_upgrade_notes import BODY_MIX, FRICATIVE_SCALE, SEED, SOURCES, approaches, first_onsets, inhales, layout, pressure, tension, vibrato  # noqa: E402

REST = 0
HOLD, BREATH = 1.25, .75  # a half note inside the bar, leaving room for an inhale
ENGLISH = {
    "twin": "T W IH NG", "kle": "K AH L", "lit": "L IH T", "tle": "T AH L", "star": "S T AA R", "how": "HH AW", "I": "AY",
    "won": "W AH N", "der": "D ER", "what": "W AH T", "you": "Y UW", "are": "AA R", "up": "AH P", "a": "AH", "bove": "B AH V",
    "the": "DH AH", "world": "W ER L D", "so": "S OW", "high": "HH AY", "like": "L AY K", "dia": "D AY", "mond": "M AH N D",
    "in": "IH N", "sky": "S K AY",
}
# ASCII pinyin -> (engine token, intended ARPAbet phones). Raw pinyin is too coarse for the English dictionary
# (ba = B IY EY, qi = K IY, de = D IY; zhi, guai are absent), so each token is a homophone it reads as one syllable.
PINYIN = {
    "liang": ("liang", "L Y AE NG"), "zhi": ("jerr", "JH ER"), "lao": ("lao", "L AW"), "hu": ("hu", "HH UW"),
    "pao": ("pao", "P AW"), "de": ("duh", "D AH"), "kuai": ("kwai", "K W AY"), "yi": ("yi", "Y IY"), "mei": ("mei", "M EY"),
    "you": ("yo", "Y OW"), "yan": ("yen", "Y EH N"), "jing": ("jing", "JH IH NG"), "wei": ("wei", "W EY"), "ba": ("bah", "B AA"),
    "zhen": ("jun", "JH AH N"), "qi": ("chee", "CH IY"), "guai": ("gwie", "G W AY"),
}
# ARPAbet -> the dashboard's illustrative phone set, plus the label it should show.
DASH = {"ER": ("AH", "ɝ"), "OW": ("OU", "oʊ"), "JH": ("CH", "dʒ"), "P": ("B", "p"), "TSR": ("CH", "ʈʂ")}
ARPA_VOWELS = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"}
C, D, E, F, G, A = 60, 62, 64, 65, 67, 69


def line(a, b, c, d, syllables, end=False):
    tail = [(d, 3.0)] if end else [(d, HOLD), (REST, BREATH)]
    return [(n, 1.0) for n in (a, a, b, b, c, c)] + tail, syllables


def twinkle():
    open_ = "twin kle twin kle lit tle star".split()
    close = "how I won der what you are".split()
    rows = [line(C, G, A, G, open_), line(F, E, D, C, close),
            line(G, F, E, D, "up a bove the world so high".split()), line(G, F, E, D, "like a dia mond in the sky".split()),
            line(C, G, A, G, open_), line(F, E, D, C, close, end=True)]
    tokens = "twinkle twinkle little star how i wonder what you are up above the world so high like a diamond in the sky twinkle twinkle little star how i wonder what you are"
    return {"bpm": 88, "rows": rows, "lyrics": tokens, "pron": lambda s: s, "phones": lambda s: ENGLISH[s],
            "title": "Twinkle, Twinkle, Little Star (traditional)", "subtitle": "TWINKLE, TWINKLE, LITTLE STAR · VOICE UPGRADE (CHIMERA PATCH, STAGE C BODY)"}


def two_tigers():
    do, re, mi, fa, so, la, low = 63, 65, 67, 68, 70, 72, 58  # E-flat, so the top stays at Amazing Grace's C5
    q = 1.0
    bars = [
        ([(do, q), (re, q), (mi, q), (do, q)] * 2 + [(REST, q)], "liang zhi lao hu liang zhi lao hu"),
        ([(mi, q), (fa, q), (so, q), (REST, q)] * 2, "pao de kuai pao de kuai"),
        ([(so, .5), (la, .5), (so, .5), (fa, .5), (mi, q), (do, q), (REST, q)], "yi zhi mei you yan jing"),
        ([(so, .5), (la, .5), (so, .5), (fa, .5), (mi, q), (do, q), (REST, q)], "yi zhi mei you wei ba"),
        ([(do, q), (low, q), (do, q), (REST, q), (do, q), (low, q), (do, 3.0)], "zhen qi guai zhen qi guai"),
    ]
    rows = [(n, s.split()) for n, s in bars]
    return {"bpm": 100, "rows": rows, "lyrics": " ".join(PINYIN[s][0] for _, ss in rows for s in ss), "pron": lambda s: PINYIN[s][0], "phones": lambda s: PINYIN[s][1],
            "title": "Two Tigers (traditional, to Frere Jacques)", "subtitle": "TWO TIGERS · VOICE UPGRADE (CHIMERA PATCH, STAGE C BODY)", "pinyin": True}


def stressed(phones):
    return " ".join(p + "1" if p in ARPA_VOWELS else p for p in phones.split())


def pinyin_lexicon(rows):
    """Pinyin spelling rules on the phone-level path: -ang is a back vowel plus /ŋ/, zh- the unaspirated retroflex affricate."""
    out = {}
    for s in sorted({s for _, ss in rows for s in ss}):
        phones = PINYIN[s][1].split()
        if s.endswith("ang"):
            phones[-2] = "AA"
        if s.startswith("zh"):
            phones[0] = "TSR"
        if phones != PINYIN[s][1].split():
            out[s] = " ".join(phones)
    return out


def dash(phones):
    mapped = [DASH.get(p, (p, None)) for p in phones.split()]
    return [m[0] for m in mapped], [m[1] for m in mapped]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("song", choices=["twinkle", "two_tigers"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--rules", action="store_true", help="turn on the engine's phonology rules and the pinyin lexicon")
    ap.add_argument("--plan", help="segments JSON of a --plan-only engine pass: ends each inhale before the phrase's first consonant")
    args = ap.parse_args()
    song = {"twinkle": twinkle, "two_tigers": two_tigers}[args.song]()
    lexicon = pinyin_lexicon(song["rows"]) if args.rules and song.get("pinyin") else {}
    if lexicon:
        tok = {s: (s if s in lexicon else PINYIN[s][0]) for s in PINYIN}
        song.update(lyrics=" ".join(tok[s] for _, ss in song["rows"] for s in ss), pron=tok.__getitem__, phones=lambda s: lexicon.get(s, PINYIN[s][1]))
    notes = [list(n) for row, _ in song["rows"] for n in row]
    syllables = [s for _, ss in song["rows"] for s in ss]
    assert sum(n[0] > 0 for n in notes) == len(syllables), (len(notes), len(syllables))
    j = {"bpm": song["bpm"], "t0": 1.0, "vibrato": 35, "lyrics": song["lyrics"], "notes": notes}
    rng = np.random.default_rng(SEED)
    phrases = layout(j)
    mean_midi = float(np.mean([n["midi"] for p in phrases for n in p]))
    gestures = [g for p in phrases for g in pressure(p, mean_midi)] + inhales(phrases, j["t0"], first_onsets(phrases, json.loads(Path(args.plan).read_text())) if args.plan else None) + vibrato(phrases, rng, True) + approaches(phrases) + tension(phrases, mean_midi)
    j.update(bodyMix=BODY_MIX, source=SOURCES["C"], fricativeScale=FRICATIVE_SCALE, externalVibrato=True, gestures=gestures)
    if args.rules:
        j["phonologyRules"] = True
        if lexicon:
            j["lexicon"] = {w: stressed(p) for w, p in lexicon.items()}
    out = Path(args.out)
    out.with_suffix(".notes.json").write_text(json.dumps(j, indent=1) + "\n")
    timed = [n for p in phrases for n in p]
    rows = []
    for s, n in zip(syllables, timed):
        phones, display = dash(song["phones"](s))
        rows.append({"grapheme": s, "pron": song["pron"](s), "phones": phones, "display": display, "notes": 1, "start": n["start"], "end": n["end"]})
    out.with_suffix(".lyrics.json").write_text(json.dumps({"title": song["title"], "subtitle": song["subtitle"], "syllables": rows}, indent=1, ensure_ascii=False) + "\n")
    print(f"{out.name}: {len(syllables)} sung notes, {len(gestures)} gestures in {len(phrases)} phrases")


if __name__ == "__main__":
    main()
