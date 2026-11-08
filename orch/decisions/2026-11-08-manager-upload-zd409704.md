# Manager decision — upload singing-vocal-path-viz to GitHub zd409704

Date: 2026-11-08 Asia/Shanghai
From: Claude Manager
To: Claude 4 (program lead for singing-vocal-path-viz)

## Decision

Owner directed: upload this program to GitHub. Research uploads go under account zd409704 (not DavidZhang-HT). Create a new public repository `zd409704/singing-vocal-path-viz` and push a lean snapshot of the sealed demo tree.

Authorized by owner chat: upload this project to GitHub.

## Scope

- Program root: `/srv/claude/research/singing-vocal-path-viz/`
- Local tree currently has no `.git`. Initialize as needed.
- Preferred remote: `https://github.com/zd409704/singing-vocal-path-viz`
- Visibility: public
- Default branch: `main`
- Sealed demo already verified by Manager: `results/vocal_path_demo.mp4` sha256 `da1ec279026f04e9bdaefdc056b224359a018033d3bcb971f9f33ffc40b90baf`

## Include

- Source: `pipeline/`, `render/` (JS and package files only), `docs/`, `run_pipeline.sh`, and `demo/` if useful
- Demo audio: `assets/demo_audio/` (synthesized clip, lyrics, synthesizer truth)
- Sealed results: `results/vocal_path_demo.mp4`, `results/vocal_path_demo.html`, `results/vocal_path_audio.m4a`, `results/analysis.json`, `results/analysis_metrics.json`
- Notes: `STATUS.md`, `notes/MATERIAL.md`, `notes/METHOD.md`, `notes/DEMO_AUDIO.md`, `notes/reference/SOURCE.md`
- Optional: `notes/reference/frames/` (layout stills, no audio)
- `orch/decisions/` and `orch/prompts/` (small). Skip bulky orch logs.
- A short `README.md` covering how to run, what is measured vs illustrative, and the audio source.
- A short `GITHUB-CONTENTS.md` listing what was omitted and why.

## Exclude (hard)

- `.venv/`
- `render/node_modules/`
- `results/qc/` (includes a browser profile)
- `results/preview/` and `results/preview2/`
- `__pycache__/`, `*.pyc`
- `notes/reference/source-post-2119421849134305644.mp4` and any other copy of the visual-reference video or its soundtrack. That file is layout reference only; its soundtrack must not be uploaded or redistributed.
- Do not decode, extract, or commit audio from the reference video.

## Constraints

- Stay under the program root for writes (except git remotes / GitHub API needed for this upload).
- Scan the commit for secrets and tokens before pushing.
- Do not add Co-authored-by trailers that attribute the work to DavidZhang-HT or any other account that standing rules keep off zd409704 research repos.
- Do not name commercial robot or company brands in new files written for the upload.
- Do not start a new research packet or rerun the demo pipeline unless a listed deliverable is missing (the sealed files already exist).
- SuperMimic remains STOP. Other programs stay untouched.

## Auth

Use the owner's GitHub access for zd409704. The motion-style-slider-repro upload used Mac `gh` authenticated as zd409704. Box `gh` on the shared computer is logged in as DavidZhang-HT — do not use it to create or push this repository. If zd409704 access is blocked, stop and report the exact blocker. Do not fall back to DavidZhang-HT.

## Report

Report back to Manager with: HTTPS URL, visibility, default branch, HEAD commit sha, approximate pushed size, and the path of `GITHUB-CONTENTS.md`. Then idle HOLD.
