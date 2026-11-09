#!/usr/bin/env python3
"""Loopback backend for the comparative voice page: renders the selected pinned engine for real.

Run with: .venv/bin/python tools/vm/server.py [port]. Binds 127.0.0.1 only. Writes only under results/voice_mechanisms/.
"""
import hashlib
import json
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/vm"))
import score as score_mod  # noqa: E402
import paths  # noqa: E402

REGISTRY = json.loads((ROOT / "versions/registry.json").read_text())
VERSIONS = {v["id"]: v for v in REGISTRY["versions"]}
RENDERS = ROOT / "results/voice_mechanisms/renders"
SCORES = ROOT / "results/voice_mechanisms/scores"
PAGE = ROOT / "tools/vm/page.html"
SLOTS = threading.Semaphore(3)
LOCK = threading.Lock()


def python_bin():
    """Room render uses the interpreter that has numpy, scipy, and soundfile.

    A project .venv is used when it exists. Otherwise the interpreter that
    launched this server is used, so a missing local .venv is not required.
    """
    venv = ROOT / ".venv/bin/python"
    return str(venv if venv.is_file() else Path(sys.executable))


def pinned_binary_sha(checkpoint):
    for line in (ROOT / "versions" / checkpoint / "SHA256SUMS").read_text().splitlines():
        if not line.strip():
            continue
        digest, name = line.split()
        if name == "chimera":
            return digest
    return None


def public_versions():
    """Registry presets plus whether this publication can build each checkpoint."""
    out = []
    for v in REGISTRY["versions"]:
        info = paths.checkpoint_info(v["checkpoint"])
        out.append({**v, "sourceInRepo": info["sourceInRepo"], "reconstructable": info["reconstructable"], "reason": info["reason"]})
    return out


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def set_path(obj, path, value):
    keys = path.split(".")
    for k in keys[:-1]:
        obj = obj.setdefault(k, {})
    obj[keys[-1]] = value


def get_score(score):
    key = score_mod.score_key(score)
    d = SCORES / key
    f = d / "notes.json"
    with LOCK:
        if not f.exists():
            j = score_mod.build(score, d / "work")
            f.write_text(json.dumps(j, sort_keys=True))
    return json.loads(f.read_text()), key


def apply_model(notes, side):
    """Model settings onto a copy of the shared score. Returns the notes and what was and wasn't applied."""
    v = VERSIONS.get(side.get("version"))
    if not v:
        raise ValueError(f"unknown version {side.get('version')!r}")
    notes = json.loads(json.dumps(notes))
    applied, ignored = {}, {}
    base_defs = {p["key"]: p for p in REGISTRY["baseParams"]}
    for key, val in (side.get("base") or {}).items():
        p = base_defs.get(key)
        if p is None:
            raise ValueError(f"unknown base parameter {key!r}")
        if v["kind"] == "upstream":
            ignored[key] = "upstream binary does not read this"
            continue
        set_path(notes, p["path"], val)
        applied[key] = val
    if v["kind"] == "mech":
        allowed = REGISTRY["checkpointMechanisms"][v["checkpoint"]]
        mech = json.loads(json.dumps(v["mech"]))
        for group, params in (side.get("mech") or {}).items():
            if group not in allowed:
                ignored[group] = f"not in checkpoint {v['checkpoint']}"
                continue
            mech.setdefault(group, {}).update(params)
        for group, on in (side.get("ablate") or {}).items():
            if group not in allowed:
                ignored[f"ablate.{group}"] = f"not in checkpoint {v['checkpoint']}"
            else:
                mech.setdefault(group, {})["enabled"] = bool(on)
        if side.get("engineSeed") not in (None, ""):
            mech["engineSeed"] = int(side["engineSeed"])
        notes["mech"] = mech
        applied["mech"] = mech
    elif side.get("mech") or side.get("ablate") or side.get("engineSeed") not in (None, ""):
        ignored["mech"] = f"{v['id']} has no mechanisms or engine seed"
    return notes, applied, ignored


def metrics(path, trace):
    y, sr = sf.read(path, dtype="float64")
    frame = int(.02 * sr)
    rms = np.array([np.sqrt(np.mean(y[i:i + frame] ** 2)) for i in range(0, max(1, len(y) - frame), frame)])
    gate = rms > 10 ** (-50 / 20)
    active = 20 * np.log10(np.sqrt(np.mean(rms[gate] ** 2))) if gate.any() else -120.0
    m = {"seconds": len(y) / sr, "peak": float(np.abs(y).max()), "activeRmsDb": float(active), "nonFinite": int((~np.isfinite(y)).sum())}
    if trace:
        t = np.array(trace["rows"])
        if len(t):
            c = trace["columns"]
            voiced = t[:, c.index("voicing")] > .9
            m["voicedFraction"] = float(voiced.mean())
            if voiced.any():
                cents = 1200 * np.log2(t[voiced, c.index("f0Meas")] / t[voiced, c.index("f0Target")])
                m["pitchErrorCentsMedianAbs"] = float(np.median(np.abs(cents)))
            if "lungFraction" in c:
                m["lungFractionMin"] = float(t[:, c.index("lungFraction")].min())
    return m


def render(req):
    score = {**score_mod.DEFAULT, **(req.get("score") or {})}
    side = req["side"]
    notes, applied, ignored = apply_model(get_score(score)[0], side)
    v = VERSIONS[side["version"]]
    binary = paths.engine_binary(v["checkpoint"])
    bin_sha = sha(binary)
    expected_sha = pinned_binary_sha(v["checkpoint"])
    key = hashlib.sha256(json.dumps({"bin": bin_sha, "notes": notes, "kind": v["kind"]}, sort_keys=True).encode()).hexdigest()[:20]
    d = RENDERS / key
    meta_f = d / "meta.json"
    if meta_f.exists() and not req.get("force"):
        m = json.loads(meta_f.read_text())
        m["cached"] = True
        return m
    t0 = time.time()
    with SLOTS:
        d.mkdir(parents=True, exist_ok=True)
        nf = d / "notes.json"
        nf.write_text(json.dumps(notes, sort_keys=True))
        tmp = d / "render_tmp"
        cmd = [str(binary), "render", "notes", str(nf), str(tmp), "female"]
        trace_f = d / "trace.json"
        if v["kind"] == "mech":
            cmd += ["--mech-trace", str(trace_f)]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if p.returncode != 0:
            raise RuntimeError(f"engine failed ({p.returncode}): {p.stderr.strip() or p.stdout.strip()}")
        wav = d / "render_tmp.wav"
        new_sha = sha(wav)
        dry = d / "dry.wav"
        reproduced = None
        if dry.exists():
            reproduced = new_sha == sha(dry)
            wav.unlink()
        else:
            wav.rename(dry)
        q = subprocess.run([python_bin(), str(ROOT / "tools/finish_upgrade_audio.py"), str(dry), str(d / "room.wav")], capture_output=True, text=True)
        if q.returncode != 0:
            raise RuntimeError(f"room failed: {q.stderr.strip()}")
    trace = json.loads(trace_f.read_text()) if trace_f.exists() else None
    m = {"key": key, "version": v["id"], "label": v["label"], "checkpoint": v["checkpoint"], "binarySha256": bin_sha,
         "pinnedReleaseSha256": expected_sha, "binaryMatchesPinnedRelease": bin_sha == expected_sha,
         "binaryNote": None if bin_sha == expected_sha else "Local rebuild of this checkpoint's source. It does not match the omitted release binary hash. It is not audio from another version or a prerecorded file.",
         "score": score, "applied": applied, "ignored": ignored,
         "scoreSupport": v.get("scoreSupport"), "dry": {"url": f"/renders/{key}/dry.wav", "sha256": sha(d / "dry.wav"), **metrics(d / "dry.wav", trace)},
         "room": {"url": f"/renders/{key}/room.wav", "sha256": sha(d / "room.wav"), **metrics(d / "room.wav", None), "note": "finish_upgrade_audio.py: 3% wet small room, peak-normalised to 0.8 by that step"},
         "renderSeconds": time.time() - t0, "cached": False}
    if reproduced is not None:
        m["reproducedExisting"] = reproduced
    meta_f.write_text(json.dumps(m))
    return m


class H(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, *a):
        pass

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            b = PAGE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        elif path == "/api/registry":
            self._json(200, {**REGISTRY, "versions": public_versions(), "publication": paths.AVAIL, "songs": score_mod.SONGS, "probeTitles": {k: v["title"] for k, v in score_mod.PROBES.items()}, "scoreDefault": score_mod.DEFAULT})
        elif path.startswith("/renders/"):
            parts = path.split("/")
            ok = len(parts) == 4 and len(parts[2]) == 20 and all(c in "0123456789abcdef" for c in parts[2]) and parts[3] in ("dry.wav", "room.wav", "trace.json", "notes.json", "meta.json")
            f = RENDERS / parts[2] / parts[3] if ok else None
            if not ok or not f.exists():
                return self._json(404, {"error": "not found"})
            b = f.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav" if f.suffix == ".wav" else "application/json")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/render":
            return self._json(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > 1_000_000:
                raise ValueError("request too large")
            self._json(200, render(json.loads(self.rfile.read(n))))
        except Exception as e:
            self._json(400, {"error": f"{type(e).__name__}: {e}"})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"http://127.0.0.1:{port}/", flush=True)
    print("experimental unvalidated checkpoint; loopback only; formal tests were not green at capture", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
