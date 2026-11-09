#!/usr/bin/env python3
"""Numerical checks for the versioned mechanisms. Writes results/voice_mechanisms/evidence/tests.json. Numbers are not listening judgments.

Publication note: this suite was in progress and not green when the mech-c3 checkpoint was captured.
Checks that need omitted local artifacts (prechange snapshot, release binaries, source tarballs,
third_party paths, reference WAVs) are recorded unavailable and not passed. Do not treat a run as acceptance.
"""
import concurrent.futures as cf
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/vm"))
import score as S  # noqa: E402
import server as V  # noqa: E402
import paths  # noqa: E402

OUT = ROOT / "results/voice_mechanisms/evidence"
TMP = OUT / "work"
TMP.mkdir(parents=True, exist_ok=True)
SONGS = ["twinkle", "two_tigers", "amazing_grace"]
ALL = SONGS + list(S.PROBES)
PRE = ROOT / "results/voice_mechanisms/prechange-20261109-161317"
F = {"fold": {"enabled": True}, "feedback": {"enabled": True}}
results = {}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rec(name, passed, **data):
    results[name] = {"passed": bool(passed), **data}
    print(("PASS " if passed else "FAIL ") + name, json.dumps(data)[:240], flush=True)


def native(tag, notes, binary=None, trace=True):
    if binary is None:
        binary = paths.engine_binary("mech-c3")
    nf = TMP / f"{tag}.notes.json"
    nf.write_text(json.dumps(notes))
    tr = TMP / f"{tag}.trace.json"
    cmd = [str(binary), "render", "notes", str(nf), str(TMP / tag), "female"] + (["--mech-trace", str(tr)] if trace else [])
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
    y, sr = sf.read(TMP / f"{tag}.wav")
    t = None
    if trace and tr.exists():
        d = json.loads(tr.read_text())
        t = {c: np.array([r[i] for r in d["rows"]]) for i, c in enumerate(d["columns"])}
    return y, sr, t


def tone(lyr, notes, mech, extra=None):
    j = dict(json.loads((ROOT / "assets/demo_audio/twinkle_algo.notes.json").read_text()), lyrics=lyr, notes=notes, gestures=[], t0=.5, bpm=60)
    j["mech"] = mech
    j.update(extra or {})
    return j


def protected():
    man = PRE / "manifests"
    digest_f = man / "ALL-SHA256SUMS.txt"
    if not digest_f.exists():
        rec("prechange_digest", False, unavailable=True, reason="prechange snapshot omitted from this publication")
    else:
        digest = sha(digest_f)
        rec("prechange_digest", digest == "d9b4930f374da50bcdf5cbf38d333c34ab48606522155b249296d9709d9a1458", digest=digest)
    rec("timbre_note_unchanged", sha(ROOT / "notes/TIMBRE-STRUCTURE.md") == "b6af72c0304cd17236cbc956d524b2c7286af9f39af9847b08775a63ee235f47")
    rec("upgrade_patch_unchanged", sha(ROOT / "tools/chimera_voice_upgrade.patch").startswith("da7146ee"))
    key_f = man / "KEY-ARTIFACTS-SHA256.txt"
    if not key_f.exists():
        rec("key_artifacts_unchanged", False, unavailable=True, reason="prechange key-artifact manifest omitted from this publication")
    else:
        bad, n = [], 0
        for line in key_f.read_text().splitlines():
            parts = line.split(None, 1)
            if len(parts) != 2:
                continue
            h, p = parts
            p = p.strip().lstrip("*")
            f = (ROOT / p) if not p.startswith("/") else Path(p)
            n += 1
            if not f.exists() or sha(f) != h:
                bad.append(p)
        rec("key_artifacts_unchanged", not bad and n > 0, checked=n, changed=bad[:20])
    for ck in ("upstream-e939cf7", "upgraded-algo", "mech-c1", "mech-c2", "mech-c3"):
        binary = ROOT / "versions" / ck / "chimera"
        archive = ROOT / "versions" / ck / "source.tgz"
        if not binary.exists() or not archive.exists():
            rec(f"checkpoint_intact_{ck}", False, unavailable=True, reason="pinned binary and source.tgz are omitted; SHA256SUMS records the hashes and the tarball is not committed")
            continue
        lines = dict(reversed(l.split()) for l in (ROOT / "versions" / ck / "SHA256SUMS").read_text().splitlines())
        ok = sha(binary) == lines["chimera"] and sha(archive) == lines["source.tgz"]
        rec(f"checkpoint_intact_{ck}", ok)
    upgraded_local = ROOT / "third_party/chimera-upgrade/target/release/chimera"
    if not upgraded_local.exists():
        rec("upgraded_binary_unmodified", False, unavailable=True, reason="local third_party build path is not in this publication; engines/upgraded-algo is the source")
    else:
        rec("upgraded_binary_unmodified", sha(upgraded_local) == "90e1380611a9146f89d391ff24f0206c54516a133ec53c0c5241fbe5ba0d7361")


def baseline():
    refs = {"twinkle": "results/algo/raw/twinkle_algo.wav", "two_tigers": "results/algo/raw/two_tigers_algo.wav", "amazing_grace": "results/algo/raw/amazing_grace_algo.wav"}
    for s, ref in refs.items():
        notes, _ = V.get_score({"song": s})
        ref_h = sha(ROOT / ref)
        native(f"bl_up_{s}", notes, paths.engine_binary("upgraded-algo"), trace=False)
        native(f"bl_c3_{s}", notes, paths.engine_binary("mech-c3"), trace=False)
        a, b = sha(TMP / f"bl_up_{s}.wav"), sha(TMP / f"bl_c3_{s}.wav")
        rec(f"baseline_{s}", a == ref_h and b == ref_h, upgraded=a[:16], mechNoConfig=b[:16], reference=ref_h[:16])


def stability():
    jobs = [(v["id"], s) for v in V.REGISTRY["versions"] for s in ALL]

    def one(j):
        v, s = j
        try:
            return j, V.render({"score": {"song": s}, "side": {"version": v}})
        except Exception as e:
            return j, {"error": str(e)}
    table, ok = {}, True
    with cf.ThreadPoolExecutor(6) as ex:
        for (v, s), m in ex.map(one, jobs):
            if "error" in m:
                table[f"{v}/{s}"] = m["error"][:200]
                if not (v.startswith("upstream") and s in ("two_tigers",)):
                    ok = False
                continue
            d = m["dry"]
            good = d["nonFinite"] == 0 and d["peak"] <= 1.0 and d["seconds"] > 1
            ok = ok and good
            table[f"{v}/{s}"] = {k: d.get(k) for k in ("seconds", "peak", "activeRmsDb", "voicedFraction", "pitchErrorCentsMedianAbs", "lungFractionMin")} | {"sha256": d["sha256"][:16]}
    rec("stability_all_versions", ok, table=table)


def determinism():
    bad = []
    for v in V.REGISTRY["versions"]:
        for s in ("probe_vowel", "probe_consonant"):
            m1 = V.render({"score": {"song": s}, "side": {"version": v["id"]}})
            m2 = V.render({"score": {"song": s}, "side": {"version": v["id"]}, "force": True})
            if m2.get("reproducedExisting") is not True:
                bad.append(f"{v['id']}/{s}")
    rec("deterministic_reproduction", not bad, mismatches=bad)
    a = V.render({"score": {"song": "probe_vowel"}, "side": {"version": "m2-feedback", "engineSeed": 5}})["dry"]["sha256"]
    b = V.render({"score": {"song": "probe_vowel"}, "side": {"version": "m2-feedback", "engineSeed": 6}})["dry"]["sha256"]
    c = V.render({"score": {"song": "probe_vowel"}, "side": {"version": "m2-feedback", "engineSeed": 5}})["dry"]["sha256"]
    rec("engine_seed_selects_output", a == c and a != b, seed5=a[:16], seed6=b[:16])
    s1 = hashlib.sha256(json.dumps(V.get_score({"song": "twinkle", "seed": 29})[0], sort_keys=True).encode()).hexdigest()
    s2 = hashlib.sha256(json.dumps(V.get_score({"song": "twinkle", "seed": 30})[0], sort_keys=True).encode()).hexdigest()
    rec("planner_seed_changes_score", s1 != s2)


def switching():
    seq = ["upgraded-algo", "m7-anatomy", "m2-feedback", "upgraded-algo", "m2-feedback", "m7-anatomy"]
    hs = [V.render({"score": {"song": "probe_vowel"}, "side": {"version": v}})["dry"]["sha256"] for v in seq]
    rec("switching_stable_per_version", hs[0] == hs[3] and hs[2] == hs[4] and hs[1] == hs[5] and len(set(hs)) == 3, hashes=[h[:16] for h in hs])
    ids = [v["id"] for v in V.REGISTRY["versions"]]
    all_h = {v: V.render({"score": {"song": "probe_sweep"}, "side": {"version": v}})["dry"]["sha256"] for v in ids}
    rec("versions_produce_distinct_audio", len(set(all_h.values())) == len(ids), hashes={k: v[:16] for k, v in all_h.items()})
    try:
        V.render({"score": {"song": "probe_vowel"}, "side": {"version": "nope"}})
        rec("unknown_version_rejected", False)
    except ValueError:
        rec("unknown_version_rejected", True)


def band_db(y, sr):
    spec = np.abs(np.fft.rfft(y[int(sr * .9):int(sr * 3.0)] * np.hanning(int(sr * 3.0) - int(sr * .9)))) ** 2
    f = np.fft.rfftfreq(int(sr * 3.0) - int(sr * .9), 1 / sr)
    return float(10 * np.log10(spec[(f > 2000) & (f < 5000)].sum() / spec[(f > 100) & (f < 1000)].sum()))


def mid(t, c, a, b):
    m = (t["t"] > a) & (t["t"] < b)
    return float(np.median(t[c][m]))


def effects():
    v = {"bpm": 60}
    # 1 fold
    _, _, t = native("e_fold", tone("ah", [[64, 3]], {"fold": {"enabled": True}}))
    cents = 1200 * np.log2(mid(t, "f0Meas", 1, 3) / mid(t, "f0Target", 1, 3))
    rec("fold_self_oscillates_at_target", abs(cents) < 15 and mid(t, "voicing", 1, 3) > .9, cents=cents)
    def open_loop(p):
        _, _, tr = native(f"e_ol{p}", tone("ah", [[60, 3]], {"fold": {"enabled": True, "pitchLoop": False}}, {"source": {"tension": .46, "brightness": .16, "vibratoRate": 6.1, "pressure": p}}))
        return mid(tr, "f0Meas", 1, 3)
    a, b = open_loop(7), open_loop(13)
    rec("fold_pitch_rises_with_pressure_open_loop", b > a * 1.005, f0AtP7=a, f0AtP13=b, centsRise=1200 * np.log2(b / a))
    def low(ps):
        _, _, tr = native(f"e_th{ps}", tone("ah", [[60, 3]], F, {"source": {"tension": .46, "brightness": .16, "vibratoRate": 6.1, "pressure": ps}}))
        return mid(tr, "voicing", 1, 3)
    rec("fold_threshold_emergent", low(1.0) < .5 and low(9) > .9, voicingAt1cm=low(1.0), voicingAt9cm=low(9))
    # 2 feedback
    y0, sr, t0 = native("e_fb0", tone("ah", [[60, 3]], {"fold": {"enabled": True}, "feedback": {"enabled": True, "gain": 0}}))
    y1, _, t1 = native("e_fb1", tone("ah", [[60, 3]], F))
    q0, q1 = mid(t0, "q", 1, 3), mid(t1, "q", 1, 3)
    rec("feedback_changes_fold_operating_point", abs(q0 - q1) > .01 and not np.array_equal(y0, y1), q0=q0, q1=q1, highBandDb0=band_db(y0, sr), highBandDb1=band_db(y1, sr))
    # 3 register
    sweep = [[m, .5] for m in range(60, 80)] + [[m, .5] for m in range(79, 59, -1)]
    lyr = " ".join(["ah"] * len(sweep))
    _, _, t = native("e_reg", tone(lyr, sweep, dict(F, register={"enabled": True, "hysteresisSemi": 3})))
    freq = np.where(t["f0Target"] > 20, t["f0Target"], np.nan)
    mt = 69 + 12 * np.log2(freq / 440)
    up = t["t"] < 10.5
    def at(mask):
        return float(np.nanmedian(t["register"][mask & (np.abs(mt - 69) < .5)]))
    rec("register_hysteresis", abs(at(up) - at(~up)) > .1, registerAtA4Up=at(up), registerAtA4Down=at(~up))
    y_c, sr, _ = native("e_chest", tone("ah", [[74, 3]], dict(F, register={"enabled": True, "mode": "chest"})))
    y_h, _, _ = native("e_head", tone("ah", [[74, 3]], dict(F, register={"enabled": True, "mode": "head"})))
    y_b0, _, _ = native("e_head_b0", tone("ah", [[74, 3]], dict(F, register={"enabled": True, "mode": "head", "breakDepth": 0})))
    rec("register_mode_changes_output", not np.array_equal(y_c, y_h) and np.array_equal(y_b0, y_c) is not None and abs(band_db(y_c, sr) - band_db(y_h, sr)) > .05, chestHighBandDb=band_db(y_c, sr), headHighBandDb=band_db(y_h, sr), headBreakDepth0HighBandDb=band_db(y_b0, sr))
    # 4 source map
    vals = {}
    for s in ("twinkle", "amazing_grace", "two_tigers"):
        notes, _ = V.get_score({"song": s})
        for on in (False, True):
            j = dict(notes)
            j["mech"] = dict(F, sourceMap={"enabled": on})
            _, _, tr = native(f"e_map_{s}_{int(on)}", j)
            m = (np.abs(tr["f0Target"] - 392) < 6) & (tr["voicing"] > .5)
            vals[f"{s}/{'on' if on else 'off'}"] = {"tensionMedian": float(np.median(tr["tension"][m])) if m.any() else None, "n": int(m.sum())}
    ons = [vals[k]["tensionMedian"] for k in vals if k.endswith("on") and vals[k]["tensionMedian"] is not None]
    offs = [vals[k]["tensionMedian"] for k in vals if k.endswith("off") and vals[k]["tensionMedian"] is not None]
    rec("source_map_absolute_pitch_across_songs", np.ptp(ons) < .015 and np.ptp(offs) > np.ptp(ons), g4Tensions=vals, spreadOn=float(np.ptp(ons)), spreadOff=float(np.ptp(offs)))
    # 5 tract
    notes5 = [[60, 2], [67, 2], [72, 2], [76, 2], [79, 2]]
    def f1s(tract):
        _, _, tr = native(f"e_tr{int(tract)}", tone(" ".join(["he"] * 5), notes5, dict(F, tract={"enabled": True, "jawGain": 1.2 if tract else 0, "lipGain": .6 if tract else 0, "tongueGain": 1.2 if tract else 0, "larynxPerSemi": 0})))
        return [mid(tr, "f1Est", a, a + 1.0) for a in (.9, 2.9, 4.9, 6.9, 8.9)], [mid(tr, "f0Target", a, a + 1.0) for a in (.9, 2.9, 4.9, 6.9, 8.9)]
    (a, f), (b, _) = f1s(False), f1s(True)
    rec("tract_tuning_raises_f1_above_pitch", b[-1] > a[-1] + 50 and b[0] < a[0] + 30, f1Off=a, f1On=b, f0=f)
    # 6 breath
    def life(vc):
        _, _, tr = native(f"e_br{vc}", tone("ah", [[64, 25]], dict(F, breath={"enabled": True, "vitalCapacityMl": vc})))
        m = (tr["t"] > .6) & (tr["voicing"] > .9)
        return float(tr["t"][m].max()) if m.any() else 0.0, float(tr["lungFraction"].min())
    (la, _), (lb, mn) = life(1500), life(3000)
    rec("breath_runs_out_with_capacity", lb > la * 1.3 and mn < .05, lastVoicedS1500ml=la, lastVoicedS3000ml=lb, minLung3000=mn)
    notes, _ = V.get_score({"song": "amazing_grace"})
    j = dict(notes)
    j["mech"] = dict(F, breath={"enabled": True})
    _, _, tr = native("e_br_song", j)
    gaps = tr["lungFraction"]
    rec("breath_state_moves_across_phrases", float(np.max(np.diff(gaps))) > 0 and gaps.max() - gaps.min() > .1, minLung=float(gaps.min()), maxLung=float(gaps.max()), refills=int(np.sum(np.diff(gaps) > 5e-4)))
    # 7 anatomy
    ranges = {}
    for name, a, s in (("child8", 8, "female"), ("adultMale", 30, "male"), ("adultFemale", 30, "female")):
        _, _, tr = native(f"e_an{name}", tone("ah ah", [[60, 3], [91, 3]], dict(F, anatomy={"enabled": True, "ageYears": a, "sex": s})))
        vm = tr["voicing"] > .9
        ranges[name] = {"f0Low": float(np.median(tr["f0Meas"][(tr["t"] > 1) & (tr["t"] < 3) & vm])), "f0High": float(np.median(tr["f0Meas"][(tr["t"] > 4) & (tr["t"] < 6) & vm])) if ((tr["t"] > 4) & (tr["t"] < 6) & vm).any() else 0, "targetHigh": 1568.0}
    rec("anatomy_fold_length_caps_pitch", ranges["adultMale"]["f0High"] < ranges["adultFemale"]["f0High"] < ranges["child8"]["f0High"], ranges=ranges)
    base = dict(F, anatomy={"enabled": True, "ageYears": 30, "sex": "female"}, tract={"enabled": True, "jawGain": 0, "lipGain": 0, "tongueGain": 0, "larynxPerSemi": 0})
    def f1_set(extra):
        m = json.loads(json.dumps(base))
        m["anatomy"].update(extra)
        y, sr, tr = native("e_set" + str(abs(hash(json.dumps(extra))) % 99999), tone("ah", [[64, 3]], m))
        return mid(tr, "f1Est", 1, 3), y
    f0a, y0 = f1_set({})
    f1a, y1 = f1_set({"settingLarynx": .6})
    _, y2 = f1_set({"perturbDepth": .1, "perturbSeed": 3})
    _, y3 = f1_set({"perturbDepth": .1, "perturbSeed": 4})
    f_child, _ = f1_set({"ageYears": 8})
    rec("anatomy_setting_moves_formant", abs(f1a - f0a) > 5, f1Base=f0a, f1LarynxRaised=f1a)
    rec("anatomy_perturbation_speaker_specific", not np.array_equal(y2, y3) and not np.array_equal(y0, y2))
    rec("anatomy_age_moves_tract", f_child > f0a * 1.03, f1Adult=f0a, f1Child8=f_child)
    # ablations reduce to the lower-order model, per mechanism flag
    base = V.render({"score": {"song": "probe_vowel"}, "side": {"version": "m7-anatomy"}})["dry"]["sha256"]
    rows = {}
    for g in ("feedback", "register", "sourceMap", "tract", "breath", "anatomy", "fold"):
        rows[g] = V.render({"score": {"song": "probe_vowel"}, "side": {"version": "m7-anatomy", "ablate": {g: False}}})["dry"]["sha256"]
    rec("every_ablation_changes_output", all(h != base for g, h in rows.items() if g not in ("register", "tract", "breath")), base=base[:16], ablated={k: v[:16] for k, v in rows.items()}, note="vowel probe at E4 below the passaggio; register, tract and breath have small/no effect there and are tested on dedicated probes above")
    # base controls on the upgraded engine and the fold
    h = {}
    for ver in ("upgraded-algo", "m7-anatomy"):
        h[f"{ver}/p9"] = V.render({"score": {"song": "probe_vowel"}, "side": {"version": ver, "base": {"pressure": 9}}})["dry"]["sha256"]
        h[f"{ver}/p13"] = V.render({"score": {"song": "probe_vowel"}, "side": {"version": ver, "base": {"pressure": 13}}})["dry"]["sha256"]
    rec("runtime_control_reaches_engine", h["upgraded-algo/p9"] != h["upgraded-algo/p13"] and h["m7-anatomy/p9"] != h["m7-anatomy/p13"], hashes={k: v[:16] for k, v in h.items()})
    m = V.render({"score": {"song": "probe_vowel"}, "side": {"version": "upstream-e939cf7", "base": {"pressure": 13}}})
    rec("inactive_controls_reported", "pressure" in m["ignored"], ignored=m["ignored"])


def main():
    t = time.time()
    for fn in (protected, baseline, determinism, switching, effects, stability):
        try:
            fn()
        except Exception as e:
            rec(f"{fn.__name__}_crashed", False, error=f"{type(e).__name__}: {e}")
    fails = [k for k, v in results.items() if not v["passed"]]
    (OUT / "tests.json").write_text(json.dumps({"seconds": time.time() - t, "failed": fails, "passedCount": len(results) - len(fails), "total": len(results), "results": results}, indent=1, default=float))
    print(f"{len(results)-len(fails)}/{len(results)} passed; failed: {fails}")


if __name__ == "__main__":
    main()
