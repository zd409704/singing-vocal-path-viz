# Publication staging — voice mechanisms comparative page (mech-c3)

Staged: 2026-11-09 17:32 Asia/Shanghai
Repository target: https://github.com/zd409704/singing-vocal-path-viz ONLY
Authorization: orch/decisions/2026-11-09-owner-authorize-github-upload-voice-mechanisms.md
Decision sha256: DEC_HASH=540f3db5f0def09069b340012f072022fe17fa6953f5b151b2865a8e373f2d3a

This directory is a curated publication checkpoint for the parent CloudAgent upload. It is not a claim that anything has been uploaded. Implementation may still be running locally; this snapshot is frozen staging only. Not owner quality acceptance.

## Chosen version pin

Primary engine pin: **mech-c3**
- Source archive: versions/mech-c3-source.tgz
- sha256: 0124d50957f26829b53ec015c1422be63eeec11b14f3f2917c5ad1a4dce1a4bb
- Checkpoint SHA256SUMS: versions/mech-c3-SHA256SUMS (also records the local binary hash; binaries are omitted from this publish archive and must be rebuilt)
- Registry cumulative preset m7-anatomy uses mech-c3 (fold, feedback, register, sourceMap, tract, breath, anatomy)

Baseline pin also included for planner/A-B:
- upgraded-algo source: versions/upgraded-algo-source.tgz
- sha256: ebd031fcd6003a26519d9c80652b2371693a10bea907df61feb80b4e75d60a1a

Other registered checkpoints (upstream-e939cf7, mech-c1, mech-c2): SHA256SUMS only in this lean archive. Rebuild their binaries from the matching local checkpoints if you need every A/B lane; do not invent sources.

## Page / server (actual state)

Real loopback comparative page and server are included (not a prerecorded player):
- tools/vm/page.html — A/B UI, version select, ablations, params, score vs model controls, export/load config, dry/room, matched loudness option
- tools/vm/server.py — ThreadingHTTPServer bound to 127.0.0.1 (default port 8765)
- tools/vm/score.py — planner scores for Twinkle, Two Tigers (ASCII pinyin), Amazing Grace, and vowel/sweep/consonant probes
- versions/registry.json — version presets and parameter schema

Routes (as implemented):
- GET / — page.html
- GET /api/registry — registry + songs + probe titles
- POST /api/render — real render via pinned versions/<checkpoint>/chimera binary
- GET /renders/<20-hex>/{dry.wav,room.wav,trace.json,notes.json,meta.json}

Local test evidence at staging time: server was observed listening on http://127.0.0.1:8765/ and produced render artifacts under results/voice_mechanisms/renders/ (those WAVs are omitted here). Formal tools/vm/run_tests.py was still in progress; do not treat the suite as green in this snapshot.

## Experimental / unvalidated labels

All mech-* mechanisms are physically reduced models (two-mass fold lineage and formulaic controls). They are experimental. Listening quality is not claimed. Breath and anatomy landed in mech-c3 per registry but remain unvalidated by a finished evidence suite in this archive.

## Unmet packet scope (explicit)

- Full formal test evidence JSON may be incomplete at stage time
- upstream / mech-c1 / mech-c2 full source archives omitted for size (hashes only)
- Engine binaries omitted (rebuild required)
- Implementation notes such as VOICE-MECHANISMS-LIMITS.md may still be absent from the live tree
- STATUS on the live tree may still show VOICE_MECHANISMS_VERSIONED_START while Claude Code continues

## Setup / run (reproducible)

Dependencies: Rust toolchain for chimera CLI; Python 3 with numpy and soundfile; no network required for loopback render once binaries exist.

1. Extract versions/mech-c3-source.tgz and versions/upgraded-algo-source.tgz into working trees.
2. Build release chimera binaries in each tree (cargo build -p chimera-cli --release, matching project layout).
3. Place binaries at versions/mech-c3/chimera and versions/upgraded-algo/chimera and verify against the corresponding SHA256SUMS chimera lines.
4. For optional upstream/mech-c1/mech-c2 lanes, rebuild from the local program checkpoints and verify SHA256SUMS.
5. Install Python deps (numpy, soundfile).
6. From the program root: python tools/vm/server.py 8765
7. Open http://127.0.0.1:8765/ — loopback only; do not publish a public URL.

Score seed 29 with default tempo/transpose matches the algo planner notes for the public-domain songs included as JSON only.

## Provenance / licenses

- Engine trees include upstream LICENSE and crate Cargo.toml inside the source archives (Chimera vocal synth lineage).
- Program patch provenance: tools/chimera_voice_upgrade.patch (sha256 da7146ee489c4c731869e95bab393c5c55e7b15cabe0f61b2f7946f0ca3f5026)
- Public-domain song scores only (Twinkle; Two Tigers; Amazing Grace). No source-post soundtrack.
- Human lead recorded in program STATUS as Peter.

## Parent upload rules

Upload only to https://github.com/zd409704/singing-vocal-path-viz. Preserve existing first-demo history. No force push / reset / rebase. This staging tree is the curated content; do not push secrets, orch/logs, binaries, or source-post media.

## Integrated git layout

The branch that publishes this checkpoint unpacks the two source archives instead of committing them:

- `engines/mech-c3` matches `versions/mech-c3-source.tgz` sha256 `0124d50957f26829b53ec015c1422be63eeec11b14f3f2917c5ad1a4dce1a4bb` file-for-file (`versions/mech-c3/SOURCE-FILES.sha256`)
- `engines/upgraded-algo` matches `versions/upgraded-algo-source.tgz` sha256 `ebd031fcd6003a26519d9c80652b2371693a10bea907df61feb80b4e75d60a1a` (`versions/upgraded-algo/SOURCE-FILES.sha256`)
- Upstream commit `e939cf733f7bbaed9e5698a242b1161dc9580679` is recovered by reverse-applying `tools/chimera_voice_upgrade.patch` to `engines/upgraded-algo` (`tools/vm/reconstruct_upstream.sh`). It is not the mech-c3 tree
- mech-c1 and mech-c2 remain hash-only and are not rendered by another binary
- Build with `tools/vm/rebuild.sh`. The page calls those rebuilt binaries. See `docs/voice-mechanisms.md`

The parent upload archive that carried this staging tree is sha256 `26eeeaf014a137ac39f3690f7f20e6692ba96379c864a665c7dea0043f877e7d`. Formal `tools/vm/run_tests.py` was not green at capture. This integration does not mark it green and does not add missing physiology.

