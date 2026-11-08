# GitHub snapshot contents

Lean public archive of the sealed singing-vocal-path-viz demo, uploaded 2026-11-08.

## Included

- Source: `pipeline/`, `render/` (JavaScript and package files only), `docs/howto.md`, `run_pipeline.sh`
- Synthesized demo audio under `assets/demo_audio/` (clip, lyrics, synthesizer truth)
- Sealed demo: `results/vocal_path_demo.mp4` (sha256 da1ec279026f04e9bdaefdc056b224359a018033d3bcb971f9f33ffc40b90baf), `results/vocal_path_demo.html`, `results/vocal_path_audio.m4a`, `results/analysis.json`, `results/analysis_metrics.json`
- Notes: `STATUS.md`, `notes/MATERIAL.md`, `notes/METHOD.md`, `notes/DEMO_AUDIO.md`, `notes/reference/SOURCE.md`
- Layout stills: `notes/reference/frames/` (no audio)
- Decisions and the reproduce prompt under `orch/decisions/` and `orch/prompts/`

## Omitted, and why

- `.venv/` — local Python environment; recreate with the commands in `docs/howto.md`
- `render/node_modules/` — install with `npm install` inside `render/`
- `results/qc/`, `results/preview/`, `results/preview2/` — working leftovers (the qc tree includes a browser profile)
- `orch/logs/` — bulky orchestrator logs
- `notes/reference/source-post-2119421849134305644.mp4` — visual-reference video only; its soundtrack must not be uploaded or redistributed
- No extracted reference audio exists and none is included

This snapshot does not rerun the demo pipeline; it publishes the sealed files as they stood after DEMO_LANDED.
