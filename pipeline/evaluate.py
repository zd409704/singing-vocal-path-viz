#!/usr/bin/env python3
"""Compare the analysis against the synthesizer's own pitch and notes.

Applies only to the synthesized demo clip, since only it has a ground truth. Scores flatter
real use: a synthesized voice is easier to track than a recording of a person.
"""
import argparse
import json
from pathlib import Path

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("analysis")
    ap.add_argument("truth")
    ap.add_argument("--out", default="results/analysis_metrics.json")
    args = ap.parse_args()
    a = json.loads(Path(args.analysis).read_text())
    t = json.loads(Path(args.truth).read_text())

    # Truth pitch is stored at 100 Hz, matching the analysis grid.
    est = a["tracks"]["midi"]
    ref = t["f0_midi_voiced"]
    n = min(len(est), len(ref))
    pairs = [(e, r) for e, r in zip(est[:n], ref[:n]) if e is not None and r is not None]
    cents = np.array([(e - r) * 100 for e, r in pairs])
    ref_voiced = sum(r is not None for r in ref[:n])

    notes_est, notes_ref = a["notes"], t["notes"]
    matched_onsets, matched_pitch = [], 0
    used = set()
    for r in notes_ref:
        best, gap = None, 0.12
        for i, e in enumerate(notes_est):
            if i not in used and abs(e["start"] - r["start"]) < gap:
                best, gap = i, abs(e["start"] - r["start"])
        if best is not None:
            used.add(best)
            matched_onsets.append(gap)
            matched_pitch += notes_est[best]["midi"] == r["midi"]

    metrics = {
        "ground_truth": "synthesizer control track, not a human reference",
        "pitch": {
            "frames_compared": len(cents),
            "voiced_recall": round(len(cents) / max(1, ref_voiced), 4),
            "rms_error_cents": round(float(np.sqrt(np.mean(cents ** 2))), 2),
            "median_abs_error_cents": round(float(np.median(np.abs(cents))), 2),
            "gross_error_rate_over_50c": round(float(np.mean(np.abs(cents) > 50)), 4),
        },
        "notes": {
            "score_notes": len(notes_ref),
            "detected_notes": len(notes_est),
            "matched_within_120ms": len(matched_onsets),
            "matched_with_correct_pitch": int(matched_pitch),
            "median_onset_error_ms": round(float(np.median(matched_onsets)) * 1000, 1)
            if matched_onsets else None,
        },
        "alignment_warning": a["meta"]["alignment_warning"],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=1))
    print(json.dumps(metrics, indent=1))


if __name__ == "__main__":
    main()
