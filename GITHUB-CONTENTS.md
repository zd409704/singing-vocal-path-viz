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

## Voice-mechanism checkpoint (later commit)

Experimental and incomplete. Not owner quality acceptance. The formal numerical suite was not green when the checkpoint was captured.

### Included

- Unpacked Chimera sources: `engines/upgraded-algo`, `engines/mech-c3`, with per-file manifests under `versions/*/SOURCE-FILES.sha256`
- Upstream file manifest `versions/upstream-e939cf7/SOURCE-FILES.sha256` and `tools/vm/reconstruct_upstream.sh` (reverse of `tools/chimera_voice_upgrade.patch` onto the upgraded tree). Provenance: `engines/PROVENANCE.md`
- Hash pins for omitted mech-c1, mech-c2, and the omitted release binaries (`versions/*/SHA256SUMS`)
- `versions/registry.json` and `versions/availability.json` (which lanes this repo can build)
- Loopback page and server: `tools/vm/page.html`, `server.py`, `score.py`, `run_tests.py`, `checkpoint.sh`, `rebuild.sh`
- Planner and room tools, public-domain note/lyric/segment JSON for Twinkle, Two Tigers (ASCII pinyin), and Amazing Grace
- Research notes that were in the staging archive, plus `docs/voice-mechanisms.md`

### Omitted from that checkpoint

- `source.tgz` archives (the unpacked trees plus manifests replace them; archive sha256 values stay in `SHA256SUMS`)
- Engine binaries and `target/` build products (rebuild)
- mech-c1 and mech-c2 source (not reconstructable here; not replaced by mech-c3)
- WAV, MP4, the prechange snapshot, `orch/logs`, source-post media, credentials
- A green `tools/vm/run_tests.py` result (none existed at capture)

See `OMISSIONS.md` and `PUBLISH.md`.
