# STATUS — singing-vocal-path-viz

Public historical snapshot. The sealed first demo remains the record in the initial commit. This later note adds the voice-mechanism work as an experimental, unvalidated, incomplete checkpoint. It is not owner quality acceptance and not a claim that physiology is complete. Paths and hashes below include local artifacts that are not in this git commit (WAV, MP4, prechange snapshots, binaries, private logs). Only files present in the commit are published.


state: VOICE_MECHANISMS_VERSIONED_START
next: Claude Code implements missing mechanisms from TIMBRE-STRUCTURE with versioned models and a runnable comparative test page; report milestones to Manager. Not owner quality acceptance.
updated: 2026-11-09 17:33 Asia/Shanghai (publication staging snapshot; implementation was still in progress)
human_lead: Peter
Orchestrator Prompt: orch/prompts/VOICE_MECHANISMS_VERSIONED.txt

## Voice mechanisms versioned implementation (this packet)
- Owner (via Claude Manager, 2026-11-09 16:11 Asia/Shanghai) authorizes implementing missing voice mechanisms identified in notes/TIMBRE-STRUCTURE.md, with version management/switching and an adjustable comparative test page.
- Decision: orch/decisions/2026-11-09-manager-start-voice-mechanisms-versioned.md
  sha256: 85ab9dd44836e54eb11d34a183fb78a2763c1cc1b020e75f4796724ee6b5421f
- Orchestrator Prompt: orch/prompts/VOICE_MECHANISMS_VERSIONED.txt
  sha256: c7d214f1f6489a0ec13495b88676f06d58e0c936fafc20c77f4fb8d28e448b3c
- Prior findings (preserved, not overwritten): notes/TIMBRE-STRUCTURE.md
  sha256: b6af72c0304cd17236cbc956d524b2c7286af9f39af9847b08775a63ee235f47
- Prechange baseline snapshot: results/voice_mechanisms/prechange-20261109-161317/
  ALL-SHA256SUMS digest: d9b4930f374da50bcdf5cbf38d333c34ab48606522155b249296d9709d9a1458
  Index: results/voice_mechanisms/prechange-20261109-161317/INDEX.md
- Continue from actual current upgraded local engine (third_party/chimera-upgrade/ + tools/chimera_voice_upgrade.patch + nine phonologyRules), not the stale public snapshot.
- Scope mechanisms: fold/tissue self-oscillation; source-tract feedback; register/transitions; absolute-pitch personal source mapping; pitch-dependent tract adjustment; finite breath supply/phrase state; speaker anatomy/articulatory habits/development controls.
- Map every TIMBRE inventory gap to implemented/approximate/deferred with explicit limits. Reduced physical models OK if labelled; do not claim complete physiology.
- Stage coherent increments; test and continue within scope without another START; report real blockers.
- Version management: preserve all existing snapshots/WAV/video/notes; selectable upstream baseline / current upgraded baseline / new increments; pinned code/config IDs; non-destructive checkpoints; new outputs only; no destructive git; no auto-push.
- Comparative test page must actually control/render selected engines (not prerecorded): A/B versions and params; same score/lyrics/seed; mechanism ablations; units/ranges/defaults/reset; save/load/export config and WAV; dry vs room; matched loudness optional; visible metadata; real wiring with inactive controls marked; Twinkle, Two Tigers (ASCII pinyin), Amazing Grace, sustained vowel/pitch-sweep/consonant probes; separate score vs model; native/web as needed; loopback unless documented sanctioned sharing; no invented public URLs.
- Tests: stability, deterministic reproduction, baseline regression, version switching, real parameter effects. Numerical evidence separate from listening.
- Public-domain songs only; no source-post soundtrack; no copyrighted covers; third_party stays local; other programs untouched.
- The implementing agent cannot hear audio. No perceptual improvement claims. Implementation is not owner quality acceptance.
- Milestone plan (initial; Claude Code may refine):
  1. Inventory gaps to implement/approximate/defer plan against TIMBRE-STRUCTURE
  2. Version registry + dispatch so upstream and current upgraded baselines stay selectable
  3. Implement mechanisms in coherent increments with ablations and tests
  4. Build runnable comparative test page wired to real engines
  5. Render new-name A/B artifacts; protected-artifact checks; notes + STATUS
- Running state at capture: implementation was still in progress. Process ids, host display numbers, and private log paths are omitted from this public copy. The formal source-run test suite had not finished and is not green.

- Owner authorization (2026-11-09 17:29 Asia/Shanghai): one-time upload to https://github.com/zd409704/singing-vocal-path-viz ONLY, superseding no-auto-push for this upload via parent CloudAgent. Decision: orch/decisions/2026-11-09-owner-authorize-github-upload-voice-mechanisms.md. Staging-file sha256 before the public copy removed process details: 540f3db5f0def09069b340012f072022fe17fa6953f5b151b2865a8e373f2d3a. Not uploaded by this note.
- Publication staging (lean, not a push): results/voice_mechanisms/publish-stage-20261109-173209/ and archive results/voice_mechanisms/publish-voice-mechanisms-mech-c3-20261109-173209.tgz (11825893 bytes, sha256 f2eb5e1f91a75b8dfc31debe8149cd76e22e64f41e45c6ee0c97752f3c3a7110). Pin mech-c3 source 0124d50957f26829b53ec015c1422be63eeec11b14f3f2917c5ad1a4dce1a4bb plus upgraded-algo source; real tools/vm page+server included; binaries/WAVs/logs/source-post omitted. See PUBLISH.md and OMISSIONS.md inside the stage. Implementation continues; not owner quality acceptance.
- This git branch integrates the parent upload archive sha256 26eeeaf014a137ac39f3690f7f20e6692ba96379c864a665c7dea0043f877e7d. Source archives are unpacked under engines/ and checked with versions/*/SOURCE-FILES.sha256. The opaque tarballs, binaries, render audio, and prechange snapshot are not committed. mech-c1 and mech-c2 stay hash-only. Upstream e939cf7 is reconstructed by reversing tools/chimera_voice_upgrade.patch. Not a completed test run and not owner quality acceptance.


## GitHub
- URL: https://github.com/zd409704/singing-vocal-path-viz
- visibility: public
- default branch: main
- HEAD: 2639dfb62ddcdb59053945b6e809f10f5f051035
- approximate size: 14.3 MiB of blobs (36 files; packed bundle 13 MiB)
- contents note: GITHUB-CONTENTS.md
- uploaded: 2026-11-08 23:40 Asia/Shanghai to this repository as zd409704
- omitted locally and remotely from that snapshot: notes/reference/source-post-2119421849134305644.mp4, any reference soundtrack, .venv, render/node_modules, results/qc, results/preview, results/preview2, orch/logs
- Do not auto-push this chimera-compare packet (upstream clone and build artifacts stay local; source-post audio stays unpublished)

## Timbre and voice-structure analysis (completed; findings preserved)
- Owner asked Claude 4 to invoke Claude Code on what structures determine timbre and voice quality / vocal identity, whether the current synthesizer is complete, and how those structures change from small scale to large scale.
- Decision: orch/decisions/2026-11-09-manager-start-timbre-structure.md
- Orchestrator Prompt: orch/prompts/TIMBRE_STRUCTURE.txt
- Build on, do not merely copy: notes/VOICE-CONSTITUTION.md, notes/SYNTH-GAPS.md, notes/UPGRADE-PLAN.md, notes/SYNTH-ALGO-ROOTFIX.md
- Current engine: local upgraded physical-modeling path in third_party/chimera-upgrade/ plus the shared planner and finishing, including the algorithm-rootfix rules.
- Analysis only: no new WAV or video. Do not overwrite existing files.
- The analyzing agent cannot hear audio. Do not claim a quality acceptance or a very good voice.
- Do not use or upload the source-post soundtrack. Do not auto-push.
- Result: note written; analysis only. No new WAV or video, no code change, nothing committed or pushed. No existing render or the patch was overwritten (twinkle_algo, two_tigers_algo and tools/chimera_voice_upgrade.patch hashes re-checked and match this file).
- notes/TIMBRE-STRUCTURE.md: b6af72c0304cd17236cbc956d524b2c7286af9f39af9847b08775a63ee235f47
- Judgment: the synthesizer is not complete. Of 47 listed structures: 5 modeled, 13 approximated, 16 preset or constant, 13 lacking. Row status is a judgment against the note's definitions.
- Main missing pieces: fold tissue and self-oscillation, tract-to-fold feedback and register, pitch-dependent tract adjustment, an air supply, an absolute-pitch source mapping (the tension rule is relative to each song's mean pitch), an individual articulatory setting, and growth (the body presets are static, and the Stage C mix is an adult point between female and male).
- Limits: the analyzing agent cannot hear audio; nobody listened for this packet; no very good voice is claimed. Identity was not measured. Open-quotient ranges are derived from score files and engine formulas, not render telemetry. Cross-song H1-H2 uses the pre-rootfix nursery renders. The cause of the cross-song H1-H2 difference (Twinkle rises 7.1 dB where Amazing Grace falls 2.0 dB) is a guess. Physiology, including the developmental section, is qualitative general knowledge.

## Nursery songs (built; not a quality acceptance)
- Decision: orch/decisions/2026-11-09-manager-start-nursery-songs.md
- Notes: notes/NURSERY-SONGS.md, notes/COMPARISON-nursery-songs.md, notes/MATERIAL-nursery-songs.md
- Songs: Twinkle, Twinkle, Little Star; Two Tigers (ASCII pinyin with an ASCII phone map). Both public domain.
- Body: fictional Stage C tract (female 0.85), both songs. Child preset not rendered.
- results/vocal_path_demo_twinkle.mp4: 62bd38812641b014597c401aa060ad7ad0e42cd4db6d5ac8975563e215b18925
- assets/demo_audio/twinkle_upgrade.wav: 72ebba36374a805a5039371561765bd9bb2f563ebbc54a9f238c994951c1e4aa
- results/vocal_path_demo_two_tigers.mp4: 2275ecdd5fbbf7d35bea53d06f608c2b704017a12ce7ea76b80d720f464902fe
- assets/demo_audio/two_tigers_upgrade.wav: 9300b93ca6ec2d3513977daf010258460dc865f22d98058aa70c0dd4b868cf20
- Limits: the implementing agent cannot hear audio; owner listen is open. Two Tigers uses English phones and has no Mandarin tones. Level in rests measures higher than the Amazing Grace baselines, cause not investigated. No claim of a very good human voice; no earlier complaint claimed fixed.
- Source-post soundtrack not used, committed or uploaded. Not pushed. third_party/ stays local.

## Synthesizer algorithm root fix (built; not a quality acceptance)
- Owner asked to fix root problems in the synthesis algorithm, not only the rendered results of the two nursery songs. Claude 4 must invoke Claude Code.
- Decision: orch/decisions/2026-11-09-manager-start-synth-algo-rootfix.md
- Orchestrator Prompt: orch/prompts/SYNTH_ALGO_ROOTFIX.txt
- Prior findings: notes/TWO-TIGERS-PRONUNCIATION.md (277883195d14ee94f4223a0a4f028aa1c3843e3ff0db3d152e13ca74f756d2d4)
- Verification renders must use new names only. Do not overwrite nursery or Amazing Grace files.
- The implementing agent cannot hear audio; do not claim a quality acceptance or that mismatches are fixed by ear.
- Do not use or upload the source-post soundtrack. Do not auto-push.
- Result: all nine rules implemented in the engine and shared planner, on behind the per-score key phonologyRules. Built; not a quality acceptance. Nobody has listened. No very good voice is claimed and no mismatch is claimed fixed by ear.
- Notes: notes/SYNTH-ALGO-ROOTFIX.md, notes/MATERIAL-synth-algo-rootfix.md. Measurements: results/algo/loci_measurements.json. Pipeline: run_pipeline_algo.sh.
- results/vocal_path_demo_twinkle_algo.mp4: 828a7856acc829594144bc9f3209d2b3255fe604c6989210849928499ab921b7
- results/vocal_path_demo_two_tigers_algo.mp4: 4a79f1460ef2d5d63abfb645aeaee0b695342efbcc3f31891c54d4972afb99f6
- assets/demo_audio/twinkle_algo.wav: 53f099abd700841ec35e10b82e3447dad060fcd64fc32c375541d262ae7ff1bd
- assets/demo_audio/two_tigers_algo.wav: 0b464985f7183366185bb6a0e5f88b8bf8fd85651874b5f1624a8e699657aa2c
- assets/demo_audio/amazing_grace_algo.wav (regression, no video): fb1da0d8b04bd27c584f5029794e464497a10cae97f9fa802ffd7c6c9c0c67f4
- tools/chimera_voice_upgrade.patch (extended): da7146ee489c4c731869e95bab393c5c55e7b15cabe0f61b2f7946f0ca3f5026; prior a062305b... kept at results/algo/chimera_voice_upgrade.before_algo.patch
- Measured limits: kuai and up release peaks and zhen frication peak went down; kle /k/ unchanged; /t/ after /l/ still seals poorly; the rules are off for speech and live notes. cargo test -p chimera and -p chimera-cli passed; wasm and app not built. Existing renders unchanged by hash; nothing committed or pushed.

## Two Tigers pronunciation (findings written; analysis packet closed)
- Owner heard four syllable mismatches on results/vocal_path_demo_two_tigers.mp4 (2275ecdd5fbbf7d35bea53d06f608c2b704017a12ce7ea76b80d720f464902fe): liang as lian, kuai as guai, jing as jin, zhen as ren.
- Addendum: owner also heard four mismatches on results/vocal_path_demo_twinkle.mp4 (62bd38812641b014597c401aa060ad7ad0e42cd4db6d5ac8975563e215b18925): twin as win (missing /t/), kle as eou (missing /k/), up as a (missing /p/), so as ou (missing /s/).
- Decision: orch/decisions/2026-11-09-manager-start-two-tigers-pronunciation.md
- Addendum decision: orch/decisions/2026-11-09-manager-add-twinkle-pronunciation.md
- Prompt: orch/prompts/TWO_TIGERS_PRONUNCIATION.txt
- Findings (all eight syllables): notes/TWO-TIGERS-PRONUNCIATION.md: 277883195d14ee94f4223a0a4f028aa1c3843e3ff0db3d152e13ca74f756d2d4
- Measurements: results/nursery/pronunciation_measurements.json: bbe428b2a394cf4fea3a622691bdb301336d81dad4780ab68987c58cf2f7c7eb (from tools/measure_nursery_pronunciation.py: ae76e308ba6f97c60389212c157ac93e000d660f4c1574be7030afce0e3497d4; read-only, no audio written)
- Limits: the implementing agent cannot hear audio, and the owner's reports were not verified by listening. Links from measurements to what the owner heard are guesses, and the note marks them. No proposed change was tested, no mismatch is fixed, and no very good voice is claimed. Breath and voicing-gate figures are reconstructed from code, not engine telemetry. Formant transitions into /ng/ were not measured reliably.
- results/nursery/two_tigers_pronunciation.json (earlier interrupted run) measured only the finished WAV; its periodic /k/ reading is a room artifact. Do not cite it for voicing through closure.
- Analysis only: no new WAV or video. Do not overwrite nursery or Amazing Grace files.
- Do not use or upload the source-post soundtrack. Do not auto-push.

## Sealed first demo (do not overwrite in place)
- Material list, claims and limits: notes/MATERIAL.md
- How-to: docs/howto.md
- Method: notes/METHOD.md
- Demo audio source and license: notes/DEMO_AUDIO.md
- results/vocal_path_demo.mp4: da1ec279026f04e9bdaefdc056b224359a018033d3bcb971f9f33ffc40b90baf
- results/vocal_path_demo.html: c4b41508ec4408faf08df6d2f13faec88aadbaa5556f795b5b98917b10b80f62
- assets/demo_audio/amazing_grace_synth.wav: eb216d8cc47ca20cff3ad3ff8b062fdbe4abfe9608d4b63f02651746fae9459a
- results/analysis.json: 8b50fd0a3d707f44122e29b18def0b93789e5e83916a33e5571f765aedf01105
- notes/MATERIAL.md: 535eb514f9f36d13d09b673115ebac581b4c3da4d4bfca0181bde80da305ecc8

## Quality fix v2 (exited; not accepted)
- The quality-fix v2 orchestrator exited after writing QUALITY_FIX_LANDED notes. Owner listen of results/vocal_path_demo_synth_v2.mp4 still heard leaky hiss and unnatural breath / phrasing. That packet is not sealed as having fixed those defects.
- Owner-listen note: notes/OWNER-LISTEN-quality-fix.md
- Orch material (measurements and claims, not an acceptance): notes/MATERIAL-quality-fix.md (b2c856606bbc8ad6774f470f5980b2f6fb232747599ebe1764f2900dd3ecfb96)
- Cause note: notes/CAUSE-quality-fix.md (61114e349b851fd2e368ed5fe76baed839a84f660357e6e5147a49e6dc082048)
- Comparison: notes/COMPARISON-source-v2.md (ee482d165a836ccd7b80c9158b812c9699363cc9259c007e8c7d9c79410437a7)
- results/vocal_path_demo_synth_v2.mp4: 5aedf88fb2cb9d0554654d0afee73954390dd0d27fc7f7394f5ab22d8f11d65e (matches amazing_grace_synth_v2.wav; not accepted)
- assets/demo_audio/amazing_grace_synth_v2.wav: d0bb1d8c887e68e6e8daf0fc083a9c2ede583fa9571f35513a6e3fb9d22a675f
- results/vocal_path_demo_v2.mp4: 85b6c14ce6ad36ea5eab0891e9ff253cda3e187c412aa6ee6382481247dad709 (local-only; source-post song)
- assets/demo_audio/source_post_audio.wav: 1b7cb7b9c05674ed22276e9e825fe2fb33d21c500420384524489a6f565ed61a (local-only; gitignored; not committed or uploaded)
- What changed in the v2 synth: S/Z/SH noise gains lowered (S 0.24 to 0.085); "found" still has rest=1 (0.714 s gap); a new rest=0.5 was added after "lost" (0.357 s gap).

## Quality fix v3 (built; not sealed; owner listen still open)
- Orchestrator wrote results/vocal_path_demo_synth_v3.mp4 and notes/CAUSE-quality-fix-v3.md plus notes/LISTEN-quality-fix-v3.md. No notes/MATERIAL-quality-fix-v3.md. Packet is not marked landed: the implementing agent cannot hear audio, and v2 had already looked fine on measurements before the owner rejected it.
- results/vocal_path_demo_synth_v3.mp4: 8ba6d9b630bdcb57544ba927e4e4e0511e600329efd4c21de1a723ea65d6b385 (43 s class; soundtrack matches amazing_grace_synth_v3.wav)
- results/vocal_path_demo_v3.mp4: 85b6c14ce6ad36ea5eab0891e9ff253cda3e187c412aa6ee6382481247dad709 (byte-identical to v2; source-song analysis path unchanged)
- Do not overwrite these files. This chimera-compare packet does not continue v3 iteration.

## Chimera compare (first version built; not a quality acceptance)
- Owner post: https://x.com/QuestionAcount/status/2119290713519403516
- Software: CHIMERA, https://github.com/jamesondh/chimera-vocal-synth (MIT)
- Public demo: https://chimera-vocal-synth.vercel.app/
- Author post: https://x.com/jamesonhodge/status/2118733265372860826
- Author repo post: https://x.com/jamesonhodge/status/2119156198830379386
- Song: Amazing Grace verse 1 (this program's public-domain demo). The owner's linked video shows a different, copyrighted song on screen; do not render that song.
- Decision: orch/decisions/2026-11-09-manager-start-chimera-compare.md
- Prompt: orch/prompts/CHIMERA_COMPARE.txt
- Result: built; not a quality acceptance. The implementing agent cannot hear audio and the owner listen is open. No formant-synth defect is claimed fixed.
- Body: adult female (matches the sealed C4 to C5 register and female formant targets).
- results/vocal_path_demo_chimera.mp4: efcbba324a5254a60b901b66552a0194753a27777ddee78dae49f08178fe3eec
- results/chimera_ui_amazing_grace.mp4: 645ebc25eb534b540ac520338380f65751aa9229a36578aa3339e24428a4ecb3 (native SING view; needs local patch tools/chimera_sing_amazing_grace.patch)
- assets/demo_audio/amazing_grace_chimera.wav: b0a5d822149f881eaffa00043078a11e862e6d4ae6be497131555dc68aeab4d4
- Comparison: notes/COMPARISON-chimera.md. Material: notes/MATERIAL-chimera-compare.md.
- Main measured points for the owner listen: every labial reaches true lip contact with a release transient; sibilants about as strong as the sealed demo and longer; 30 dB more high-band energy inside vowels than the formant synth (check by ear for breathiness or hiss); rests are near digital silence with no inhale.
- third_party/ (clone, build, local Rust 1.99.1) and results/chimera/ui_capture/ are gitignored. Nothing committed or pushed.


## Voice upgrade (this packet)
- Owner asked, after the first version completed, to consider how a human voice and voiceprint are constituted, identify what the current synthesizers are missing, propose an upgrade, implement it, and compare until a very good human vocal result is reached.
- Decision: orch/decisions/2026-11-09-manager-start-voice-upgrade.md
- Prompt: orch/prompts/VOICE_UPGRADE.txt
- Baselines to leave in place: sealed formant synth, rejected v2, unsealed v3, and the CHIMERA first-version files listed above.
- Path may be a formant-synth extension, a local CHIMERA patch, or a hybrid. Implement, do not only write a memo.
- Owner ear is the acceptance gate. The implementing agent cannot hear audio and must not claim a very good human voice.
- Do not auto-push this packet (upstream clone and build artifacts stay local; source-post audio stays unpublished).
- Result: built; not a quality acceptance. The implementing agent cannot hear audio. No very good human voice is claimed, and no owner complaint is claimed fixed.
- Path: local CHIMERA patch with an outside performance planner (tools/chimera_voice_upgrade.patch, tools/make_upgrade_notes.py, tools/finish_upgrade_audio.py, run_pipeline_upgrade.sh). Isolated in third_party/chimera-upgrade/; the CHIMERA first-version clone and files are unchanged.
- Notes: notes/VOICE-CONSTITUTION.md, notes/SYNTH-GAPS.md, notes/UPGRADE-PLAN.md, notes/COMPARISON-voice-upgrade.md, notes/MATERIAL-voice-upgrade.md.
- results/vocal_path_demo_upgrade.mp4 (Stage A): a11c4286e98aee763528f6719823a6722b879a200b86868e5e1c10b2bb0e88e9
- results/vocal_path_demo_upgrade_r1.mp4 (Stage B): 1ac2a35422e776498a57de22551b389ba1717947fe15ed2aad870c6e6c442f71
- results/vocal_path_demo_upgrade_r2.mp4 (Stage C): 0e621744e04f7caf193645a08ce98fdee1af63729702614672a2c7cc8c43b20f
- assets/demo_audio/amazing_grace_upgrade.wav: 64d7e39514249421c1e2f2fdb4bc1adbcd882c2e4916a7744c5bf07b5414ecec
- assets/demo_audio/amazing_grace_upgrade_r1.wav: 216eb20c121ac39e876bdde1ad3d42d5c8bf31d8bbbe2633064ff32c57128e14
- assets/demo_audio/amazing_grace_upgrade_r2.wav: 632047a043e35d39c6c46beccc37d8036fcce8458dda6faa0d3bc34d60c0f68c
- Main points for the owner listen: rests now hold an unvoiced airway inhale, but it is upper-band heavy and could read as hiss; /s/ is shorter but no quieter, and stands about 2.6 dB above the vowels' high band where it was 1.2 dB below (first thing to check for hiss); H1-H2 now falls with pitch by 4.0 dB in _r1 and 2.0 dB in _r2, still about 8 dB lower than upstream's singer.
- Correction found: the sibilant figures in notes/COMPARISON-chimera.md were contaminated by neighbouring vowels (real planned /s/ is 96 ms, not 249 ms). That note is left unchanged; see notes/SYNTH-GAPS.md.
- Not run: wasm build, chimera-cli tests, app rebuild. cargo test -p chimera passed. Nothing committed or pushed.

## Nursery songs (this packet)
- Owner asked for two nursery-rhyme renders with the existing voice-upgrade method (local CHIMERA patch plus planner).
- Songs: Twinkle, Twinkle, Little Star (Jane Taylor 1806 / Ah! vous dirai-je, maman; public domain); Two Tigers (traditional lyric line to Frere Jacques; score in ASCII pinyin).
- Decision: orch/decisions/2026-11-09-manager-start-nursery-songs.md
- Prompt: orch/prompts/NURSERY_SONGS.txt
- Do not overwrite sealed, v2, v3, chimera-first, or Amazing Grace voice-upgrade files listed above.
- Do not render the source-post soundtrack or other copyrighted songs.
- Owner ear remains the acceptance gate. Not a quality acceptance when built.
- Do not auto-push this packet (upstream clone and build artifacts stay local; source-post audio stays unpublished).

## Manager next
- Two-Tigers pronunciation decision: orch/decisions/2026-11-09-manager-start-two-tigers-pronunciation.md
- Twinkle pronunciation addendum: orch/decisions/2026-11-09-manager-add-twinkle-pronunciation.md
- Two-Tigers pronunciation prompt: orch/prompts/TWO_TIGERS_PRONUNCIATION.txt
- Nursery-songs decision: orch/decisions/2026-11-09-manager-start-nursery-songs.md
- Nursery-songs prompt: orch/prompts/NURSERY_SONGS.txt
- Voice-upgrade decision: orch/decisions/2026-11-09-manager-start-voice-upgrade.md
- Voice-upgrade prompt: orch/prompts/VOICE_UPGRADE.txt
- Chimera-compare decision: orch/decisions/2026-11-09-manager-start-chimera-compare.md
- Chimera-compare prompt: orch/prompts/CHIMERA_COMPARE.txt
- Quality-fix v3 decision: orch/decisions/2026-11-09-manager-start-quality-fix-v3.md
- Quality-fix v3 prompt: orch/prompts/QUALITY_FIX_V3.txt
- Prior quality-fix decision: orch/decisions/2026-11-08-manager-start-quality-fix-source-song.md
- Prior quality-fix decision sha256: 283734b7a7e64305cca2f32ff35ef766121bff7d0dc34cef860de9cd6e1eff6c
- First-demo decision: orch/decisions/2026-11-08-manager-start-reproduce-vocal-path.md
- First-demo decision sha256: ca89d7cbe77bed48ece403ec9d8c96d558c196691c64801452ae4f030c9553ed
- Upload decision: orch/decisions/2026-11-08-manager-upload-zd409704.md
- Upload decision sha256: 40d62e9510f613930273b0411c6f6afa464b9d9738ea0c5d1b17f86187551d89
- Source post: https://x.com/slashui/status/2119421849134305644
- Visual reference: notes/reference/source-post-2119421849134305644.mp4
- Audio rule: owner authorized local extract of the source-post soundtrack for reproduction and comparison; do not commit or upload that audio

## Orchestrator
- Prompt: orch/prompts/TWO_TIGERS_PRONUNCIATION.txt
- Model/effort: opus medium
