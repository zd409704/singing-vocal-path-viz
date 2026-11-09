# Upgrade plan

Analysis: `notes/VOICE-CONSTITUTION.md`, `notes/SYNTH-GAPS.md`. Written after the diagnostic renders and before any upgrade render. Cap: three implementation rounds, then report.

## Path: local CHIMERA patch plus an outside performance planner

The airway, lips and flow-driven noise already exist in CHIMERA. Rebuilding them in the formant synth would be a second, weaker CHIMERA.

**Isolation.** Work happens in `third_party/chimera-upgrade/`, a snapshot of upstream `e939cf7` with its own build directory. The baseline clone and its binary are untouched. The patch is kept in `tools/chimera_voice_upgrade.patch`. `third_party/` stays local. With no profile keys in the notes JSON, the patched build reproduces the baseline WAV byte for byte (checked with `cmp`).

**Common patch** (done before round 1): `render notes` accepts `source`, `noiseGain`, `consonantScale`, `fricativeScale`, `externalVibrato` and `gestures` in its JSON, and `--segments` writes the planner's real phone times.

## Stage A, round 1: a performer

Files: `assets/demo_audio/amazing_grace_upgrade.wav`, `results/vocal_path_demo_upgrade.mp4`. Planner: `tools/make_upgrade_notes.py`. Output chain: `tools/finish_upgrade_audio.py`.

| Change | Why | Baseline to beat |
| --- | --- | --- |
| Softer glottal closure through source settings (`tension`, `brightness`) | The vowel high band is harmonic, so the pulse is what to change. Structural: no filter or EQ | CHIMERA first: band 2 to 4 kHz and H1−H2 |
| Inhale through the airway in each rest: glottis open, negative lung pressure | Replaces digital silence with a breath made by the same tract | CHIMERA first: −132 dB rests. Sealed: unrelated noise patch |
| Pressure gestures per note: phrase arc, swell on long notes, phrase-final decay | Pressure also drives effort, so level and voice quality move together | CHIMERA first: flat phrase |
| Per-note vibrato: only on some long notes, varied depth and onset, from a fixed seed | Measured share too high and depth too uniform | CHIMERA first |
| Pitch approach on upward leaps | Notes as trajectories | CHIMERA first |
| Sung fricatives shortened by duration, not gain | v2 showed gain-only sibilant changes can pass measurement and fail by ear | CHIMERA first: /s/ 96 ms |
| Small synthetic room, no added noise floor | Phrase ends decay into a space. Does not add hiss | CHIMERA first: dry |

Fixed for all rounds: score, tempo and rests stay the sealed score's, so comparisons stay like for like.

## Stage B, round 2 (`_r1`): source follows the note

Engine patch adding score-controllable `tension` and `vibratoRate` source channels.

| Change | Why | Baseline to beat |
| --- | --- | --- |
| Per-note tension, laxer on low notes and firmer on high notes | H1−H2 should fall with pitch; upstream's singer falls about 4 dB, and the measured gap is the largest source gap | Round 1 and CHIMERA first: H1−H2 low against high |
| Per-note vibrato rate | One global rate is a uniformity the singer does not show | Round 1 |

## Stage C, round 3 (`_r2`): one consistent body, and consonants

| Change | Why | Baseline to beat |
| --- | --- | --- |
| Fixed fictional identity through a body mix (tract length between presets) and a saved profile | Voiceprint needs one anatomy, deliberately chosen, not a preset | Round 2. No real person is modelled |
| Consonants with their own timing: voiced fricative frication, /s/ turbulence balance by the teeth source | Remaining consonant gaps in `SYNTH-GAPS.md` | Round 2 |

## Comparison method for every round

1. Run this program's analysis (`pipeline/analyze_v3.py`) and render a dashboard with `render/render_video_v2.js`.
2. `tools/measure_voice_upgrade.py`: phone-window measurements for all voices.
3. `pipeline/evaluate.py` against the sealed truth notes.

Upstream's singer figures give direction only. A measurement moving the right way does not show the voice sounds better. **The owner's ear decides quality**. The implementing agent cannot hear audio.

Stop after round 3 even if measurements suggest more.
