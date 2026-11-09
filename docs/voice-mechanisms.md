# Voice mechanisms comparative page (experimental)

This page is an incomplete research checkpoint of a Chimera-based singing engine. It is not owner quality acceptance, not a claim of complete vocal physiology, and not a listening test. The models are physically reduced. Measurements are numerical probes.

The sealed first demo (`results/vocal_path_demo.mp4` and `docs/howto.md`) is a separate formant-synth dashboard. This document does not replace it.

Captured state: the formal suite `tools/vm/run_tests.py` was still in progress and was **not green**. Do not treat a partial run, or this write-up, as that suite passing.

## What you can build from this repository

| Selection | Role | Source in this repo |
| --- | --- | --- |
| `upstream-e939cf7` | Upstream Chimera baseline | Reconstruct with `tools/vm/reconstruct_upstream.sh`. Not vendored as its own tree. |
| `upgraded-algo` | Upgraded baseline and the page's planner | `engines/upgraded-algo` |
| `m1-fold`, `m2-feedback` | Early mechanism presets | **Omitted** (mech-c1 hashes only) |
| `m3-register`, `m4-sourcemap`, `m5-tract` | Later presets on the previous checkpoint | **Omitted** (mech-c2 hashes only) |
| `m6-breath`, `m7-anatomy` | Pinned mech-c3 presets | `engines/mech-c3` |

The server renders only a binary built from the selected checkpoint. It does not fall back to another version. Details and commit ids: `engines/PROVENANCE.md`.

## Prerequisites

- Rust with Cargo, edition 2024 (`rustc` 1.85 or newer). The checkpoint notes a local Rust 1.99.1. `rustup toolchain install stable` is enough to compile. The wasm/browser UI of Chimera is not required for this page.
- Python 3 with `numpy`, `scipy`, and `soundfile`.
- `patch`, for the upstream reconstruction only.
- No network is required for loopback rendering after the crates are downloaded and the binaries exist. The first Cargo build does need the registry.

A project `.venv` is optional. `tools/vm/server.py` uses `.venv/bin/python` when that file exists, and otherwise the Python that launched the server.

## Rebuild and version selection

From the repository root:

```sh
tools/vm/verify_sources.sh
tools/vm/rebuild.sh release
```

`rebuild.sh` builds `upgraded-algo` and `mech-c3` with `cargo build -p chimera-cli --profile release` and installs:

- `versions/upgraded-algo/chimera`
- `versions/mech-c3/chimera`

Those binaries are gitignored. After a build, the script prints whether the binary matches the omitted release hash in `versions/<id>/SHA256SUMS`. A mismatch means this compiler did not reproduce that binary. The page still calls the binary built from the pinned source.

Pass `debug` instead of `release` for a faster compile of the same source. Debug output will not match the pinned release hash.

Upstream, only if that lane is needed:

```sh
tools/vm/reconstruct_upstream.sh
# then the cargo command the script prints, and install versions/upstream-e939cf7/chimera
```

mech-c1 and mech-c2 have no reconstruct command. Their presets stay listed and refuse to render.

`versions/registry.json` is the captured preset and parameter schema. `versions/availability.json` says which of those checkpoints this publication can build. The two files together are what `GET /api/registry` returns.

## Run the loopback page

```sh
python3 tools/vm/server.py 8765
```

Open `http://127.0.0.1:8765/` on the same machine. The server binds `127.0.0.1` only. Do not publish that URL.

Routes, as implemented:

- `GET /` — `tools/vm/page.html`
- `GET /api/registry` — presets, parameters, songs, and which checkpoints are vendored
- `POST /api/render` — one real render of the selected checkpoint
- `GET /renders/<20-hex>/{dry.wav,room.wav,trace.json,notes.json,meta.json}`

`POST /api/render` plans the score with the **upgraded-algo** binary (`--plan-only`), then renders the selected side with that side's own binary. Room output is `tools/finish_upgrade_audio.py` (a short synthetic room on the dry WAV, not a different voice).

Songs are public domain only: Twinkle, Twinkle, Little Star; Two Tigers in ASCII pinyin; Amazing Grace; plus vowel, sweep, and consonant probes. Seed 29 with tempo 1 and transpose 0 is the planner setting that matches the included `*_algo` note JSON. No other repertoire is added here.

Score controls (piece, seed, transpose, tempo) are separate from model controls. Mechanism switches that a checkpoint does not contain are marked inactive. Upstream ignores the planner's extra parameters and the server reports them as ignored.

## Known limits

- Fold, feedback, register, source map, tract, breath, and anatomy are reduced controls. Fry, period doubling, and a full tissue model are not claimed.
- With fold enabled, open quotient and closure come from the fold. The older pulse knobs do not act. The page states this.
- Listening quality is not claimed. The agent that captured the checkpoint could not hear the audio. Numerical traces are not acceptance.
- `tools/vm/run_tests.py` still expects omitted references for several checks (prechange snapshot, `results/algo/raw/*.wav`, committed `source.tgz`, a `third_party/` binary). Those checks record `unavailable` and do not pass. Rendering checks need the rebuilt binaries and were not a finished green run at capture.
- A local rebuild may not match `789f8747…` (mech-c3) or `90e13806…` (upgraded-algo). Metadata field `binaryMatchesPinnedRelease` is the place that fact is reported.
- Cargo dependencies are not vendored. The first build needs crates.io. Golden fixtures under `crates/chimera/tests/golden/` are upstream test data, included so the unpacked tree matches the pinned archive. They are not this project's demo soundtrack.
- Many notes named from earlier packets (comparison write-ups, extra decisions, prompts, WAV, MP4) were not in the staging archive and are not in this commit. `STATUS.md` is a historical snapshot and says so.

## Outstanding scope

Not done in this publication, and not finished by the checkpoint:

- mech-c1 and mech-c2 source and binaries
- the prechange snapshot and its protected-artifact manifest
- a completed, green `tools/vm/run_tests.py` run
- bit-reproducible release binaries across machines
- any claim that breath, anatomy, or the rest of the mechanism list matches a singer
- owner listening acceptance

## License

Engine trees: MIT, Jameson Hodge, `LICENSE` inside each tree. Program patch: `tools/chimera_voice_upgrade.patch`. Song text used here is public domain (Amazing Grace text 1779 / tune 1829; Twinkle; Two Tigers as ASCII pinyin). The source-post layout video and its soundtrack are not included. See `OMISSIONS.md`.
