#!/usr/bin/env bash
# Audio in, analysis, video and local page out.
# Usage: ./run_pipeline.sh [audio.wav] [lyrics.json]
# With no arguments, regenerates and uses the synthesized demo clip.
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
DEMO=assets/demo_audio/amazing_grace_synth
if [ $# -eq 0 ]; then
  "$PY" pipeline/synth_demo_voice.py --out "$DEMO.wav"
  AUDIO="$DEMO.wav"; LYRICS="$DEMO.lyrics.json"
else
  AUDIO="$1"; LYRICS="${2:-}"
fi
"$PY" pipeline/analyze.py "$AUDIO" ${LYRICS:+--lyrics "$LYRICS"} --out results/analysis.json
if [ $# -eq 0 ]; then
  "$PY" pipeline/evaluate.py results/analysis.json "$DEMO.truth.json" --out results/analysis_metrics.json
fi
NODE_PATH=render/node_modules node render/render_video.js --data results/analysis.json --audio "$AUDIO" --out results/vocal_path_demo.mp4
ffmpeg -y -loglevel error -i "$AUDIO" -c:a aac -b:a 192k results/vocal_path_audio.m4a
"$PY" pipeline/build_page.py --data results/analysis.json --out results/vocal_path_demo.html
