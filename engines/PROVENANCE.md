# Engine provenance

Experimental checkpoint. Not a finished physiology and not a listening acceptance.

The comparative page keeps three roles distinct. A later tree is never substituted for an earlier one.

## Upstream baseline `upstream-e939cf7`

Public project: [jamesondh/chimera-vocal-synth](https://github.com/jamesondh/chimera-vocal-synth), MIT, copyright 2026 Jameson Hodge. See `engines/upgraded-algo/LICENSE` (the same LICENSE text as upstream).

Exact commit verified while preparing this branch:

`e939cf733f7bbaed9e5698a242b1161dc9580679`

https://github.com/jamesondh/chimera-vocal-synth/commit/e939cf733f7bbaed9e5698a242b1161dc9580679

That commit is not vendored as a second tree. It is reconstructed from this repository:

1. Copy `engines/upgraded-algo`.
2. Reverse-apply `tools/chimera_voice_upgrade.patch` (`patch -R -p1`).
3. Check the result against `versions/upstream-e939cf7/SOURCE-FILES.sha256`.

`tools/vm/reconstruct_upstream.sh` does those steps. When this branch was prepared, the reconstructed tree was file-identical to a checkout of that commit (`diff -rq` reported no differences, 255 files).

The omitted local archive hash in `versions/upstream-e939cf7/SHA256SUMS` is `75a1f82e3fcbec1a026494bdb9dc433c4cb1941b53610d9b99dc7bb38508df34` for `source.tgz` and `e312563e13791fb4a9224876bfb24880ed40d1c4ebe99fc329dbbada5cfe67fc` for the `chimera` binary. Those tar and binary bytes were not in the publication archive, so this branch does not claim a re-tar matches that archive hash. The file-content manifest is the check that is actually reproducible here.

The upstream binary reads only bpm, lyrics, notes, vibrato, and t0. Planner gestures and mechanism flags do not apply to it. Selecting it before its own binary has been built fails the render. The server does not run upgraded-algo or mech-c3 in that slot.

## Upgraded baseline `upgraded-algo`

Unpacked source: `engines/upgraded-algo`.

Pinned archive sha256: `ebd031fcd6003a26519d9c80652b2371693a10bea907df61feb80b4e75d60a1a` (`versions/upgraded-algo/SHA256SUMS`). The tarball is not committed. `versions/upgraded-algo/SOURCE-FILES.sha256` lists every unpacked file and was checked against that archive (256 files, no mismatches).

This tree is the upstream commit plus `tools/chimera_voice_upgrade.patch` (sha256 `da7146ee489c4c731869e95bab393c5c55e7b15cabe0f61b2f7946f0ca3f5026`). Applying that patch forward to the reconstructed upstream tree reproduced `engines/upgraded-algo` with no file differences when this branch was prepared.

It is the planner engine for the page (`--plan-only` / `--segments`). It has the nine phonology rules and no mech-c3 mechanisms.

Omitted release binary hash: `90e1380611a9146f89d391ff24f0206c54516a133ec53c0c5241fbe5ba0d7361`.

## Pinned mechanisms `mech-c3`

Unpacked source: `engines/mech-c3`.

Pinned archive sha256: `0124d50957f26829b53ec015c1422be63eeec11b14f3f2917c5ad1a4dce1a4bb`. File manifest: `versions/mech-c3/SOURCE-FILES.sha256` (257 files, matched the archive).

Relative to upgraded-algo, only these paths differ:

- `crates/chimera/src/airway/network.rs`
- `crates/chimera/src/lib.rs`
- `crates/chimera/src/sources/glottis.rs`
- `crates/chimera/src/voice/human_airway.rs`
- `crates/chimera/src/voice/human_voice.rs`
- `crates/chimera/src/voice/mech.rs` (only in mech-c3)
- `crates/chimera-cli/src/render.rs`

Those edits are a reduced two-mass fold lineage and formulaic controls (fold, feedback, register, source map, tract, breath, anatomy). They are experimental. Breath and anatomy are present in this checkpoint and were not validated by a finished evidence suite.

Omitted release binary hash: `789f87471bf518315886bd6e311d2c406d5e92e3c0c750c7912776f0f5a99874`.

Presets `m6-breath` and `m7-anatomy` use this checkpoint. Presets `m1`–`m5` do not: they are registered on mech-c1 and mech-c2.

## Omitted `mech-c1` and `mech-c2`

`versions/mech-c1/SHA256SUMS` and `versions/mech-c2/SHA256SUMS` record binary and source-archive hashes only. The archives were not in the publication snapshot. They cannot be rebuilt from mech-c3, and this repository does not pretend they can. The page lists those presets so the registry stays honest, and render calls for them fail until someone supplies the matching omitted source.

| checkpoint | chimera sha256 | source.tgz sha256 |
| --- | --- | --- |
| mech-c1 | `78f9d9260321e32c502d142a59561c0d2c32b2a0ac183bd6de4c77198af91d5a` | `7c263d208857413e9e6f38483a67d4b0ad2bb168043dc83de5969a820ad0a40b` |
| mech-c2 | `525265873b773329ed54945dea7f0c8b453695840515733d5f8df11973dd8208` | `ae375e38e6595d4527574be7bd8a744930d8bfd41138c019d7a560e1b4b01d89` |

## What a local rebuild proves

`tools/vm/rebuild.sh` compiles `chimera-cli` from the vendored trees and installs `versions/<id>/chimera`. A rebuild is this source. It is not a prerecorded WAV. Bit-identity with the omitted release hash depends on the compiler and is reported on the render metadata as `binaryMatchesPinnedRelease`. A mismatch is a toolchain gap, not permission to swap checkpoints.

Bundled third-party files inside the engine trees keep their own licenses (CMU dictionary, fonts). See each tree's README.
