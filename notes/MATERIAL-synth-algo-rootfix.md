# Material: synthesizer algorithm root fix

**This is not a quality acceptance.** The implementing agent cannot hear audio. No very good voice is claimed and no owner-heard mismatch is claimed fixed. Details: `notes/SYNTH-ALGO-ROOTFIX.md`.

Public-domain scores only. The source-post soundtrack was not used. Nothing was committed or pushed. `third_party/` stays local.

## New renders

| File | sha256 |
| --- | --- |
| `results/vocal_path_demo_twinkle_algo.mp4` | `828a7856acc829594144bc9f3209d2b3255fe604c6989210849928499ab921b7` |
| `results/vocal_path_demo_two_tigers_algo.mp4` | `4a79f1460ef2d5d63abfb645aeaee0b695342efbcc3f31891c54d4972afb99f6` |
| `assets/demo_audio/twinkle_algo.wav` | `53f099abd700841ec35e10b82e3447dad060fcd64fc32c375541d262ae7ff1bd` |
| `assets/demo_audio/two_tigers_algo.wav` | `0b464985f7183366185bb6a0e5f88b8bf8fd85651874b5f1624a8e699657aa2c` |
| `assets/demo_audio/amazing_grace_algo.wav` (regression, no video) | `fb1da0d8b04bd27c584f5029794e464497a10cae97f9fa802ffd7c6c9c0c67f4` |
| `assets/demo_audio/twinkle_algo.notes.json` | `a8890d1883777465192d923e2a9de723d5e16443fb16c756312f4e31b1303f6e` |
| `assets/demo_audio/two_tigers_algo.notes.json` | `43a34ff04e4e626cf9c327a18af1d8a123fcfb01a9647cac67a559e2df136627` |
| `assets/demo_audio/amazing_grace_algo.notes.json` | `8cd761938a97b802451854513c22f1003f0acf7188de6e5840d946a4fd89548f` |
| `results/algo/loci_measurements.json` | `6b04b15bf2571ba9931d054c6cee79305729ae35076a9a4e6d4b5de205417eb5` |

Dry renders and articulator traces are in `results/algo/`.

## Code

| File | sha256 |
| --- | --- |
| `tools/chimera_voice_upgrade.patch` (extended) | `da7146ee489c4c731869e95bab393c5c55e7b15cabe0f61b2f7946f0ca3f5026` |
| `tools/make_upgrade_notes.py` (extended) | `f2b478fb3379f41eaf8f125899dcadb176a7f46164de4b9e9ac57b8764360724` |
| `tools/make_nursery_notes.py` (extended) | `c533c87ebfd367c347f4098f323755f04a16724e76eb6eeb4b7c41b1db3b56e2` |
| `tools/measure_algo_rootfix.py` (new) | `0601f21a7f291d24c01541d0ab531cbe077b4ea4f25ae3d0ef74159792f1d2d1` |
| `run_pipeline_algo.sh` (new) | `9ea2d45365259c9992f36c5f66471b7ee8d3cac1fab815624fddf473849b1829` |

The prior patch (`a062305b540c4f40134ba59c00acd7a87ddcba4a575432293514c5c16d1662a6`) is kept at `results/algo/chimera_voice_upgrade.before_algo.patch`. The extended patch keeps its changes; one old line differs because that call gained the `rules` argument. Applied with `patch -p1` to upstream snapshot `a937cf2`, it reproduces `third_party/chimera-upgrade/crates` exactly.

## Existing files

`results/algo/protected_before.sha256` holds 51 hashes taken before any render: existing demo WAVs and JSON, existing videos, nursery dry renders, and the three tool files. Rechecked after the renders, 48 match. The 3 that differ are the files this packet was to extend: the patch and the two planner scripts.

Without `--rules` the two planner scripts still write byte-identical score files (checked for Twinkle, Two Tigers and Amazing Grace stage C). The upstream clone `third_party/chimera-vocal-synth` was not written to.
