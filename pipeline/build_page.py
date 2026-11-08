#!/usr/bin/env python3
"""Build a single local HTML player: renderer and analysis inlined, audio alongside."""
import argparse
import json
from pathlib import Path

TEMPLATE = """<!doctype html>
<meta charset="utf-8"><title>VOCAL PATH</title>
<style>
 html,body{margin:0;height:100%;background:#0a0d12;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px}
 canvas{max-width:100vw;max-height:calc(100vh - 60px)}
 audio{width:min(900px,90vw)}
</style>
<canvas id="c" width="1920" height="1080"></canvas>
<audio id="a" controls src="__AUDIO__"></audio>
<script>__RENDERER__</script>
<script>
 const data = __DATA__;
 const canvas = document.getElementById("c"), ctx = canvas.getContext("2d"), audio = document.getElementById("a");
 const draw = VocalPath.createDashboard(data, (w, h) => Object.assign(document.createElement("canvas"), {width: w, height: h}));
 (function loop() { draw(ctx, audio.currentTime); requestAnimationFrame(loop); })();
</script>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default="results/analysis.json")
    ap.add_argument("--renderer", default="render/dashboard.js")
    ap.add_argument("--audio", default="vocal_path_audio.m4a", help="path relative to the page")
    ap.add_argument("--out", default="results/vocal_path_demo.html")
    args = ap.parse_args()
    data = json.loads(Path(args.data).read_text())
    page = (TEMPLATE.replace("__AUDIO__", args.audio)
            .replace("__RENDERER__", Path(args.renderer).read_text())
            .replace("__DATA__", json.dumps(data)))
    Path(args.out).write_text(page)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
