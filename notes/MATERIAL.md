# MATERIAL: singing-vocal-path-viz

Sealed 2026-11-08 23:27 Asia/Shanghai. Human lead: Peter.

## Artifacts

| File | What it is | sha256 |
| --- | --- | --- |
| `results/vocal_path_demo.mp4` | Demo video, 1920x1080, 30 fps, 43.4 s, with audio | `da1ec279026f04e9bdaefdc056b224359a018033d3bcb971f9f33ffc40b90baf` |
| `results/vocal_path_demo.html` | Local player page | `c4b41508ec4408faf08df6d2f13faec88aadbaa5556f795b5b98917b10b80f62` |
| `results/vocal_path_audio.m4a` | Audio for the page, encoded from the demo clip | `d243431b99eeea37b5fc8497c6e2ac753b704e3f97043d44b3ed9c8bb5140f3d` |
| `results/analysis.json` | Analysis driving the dashboard | `8b50fd0a3d707f44122e29b18def0b93789e5e83916a33e5571f765aedf01105` |
| `results/analysis_metrics.json` | Pitch and note scores against synthesizer truth | `695ab17fe51abec61d25c520c3dd6e0d369122aa933b0631fa1b9f4db73ee281` |
| `assets/demo_audio/amazing_grace_synth.wav` | Demo audio | `eb216d8cc47ca20cff3ad3ff8b062fdbe4abfe9608d4b63f02651746fae9459a` |
| `assets/demo_audio/amazing_grace_synth.lyrics.json` | Lyric text input | `54403259f940b2ac8e68b670d6239d30226138a0fa858cb2d50bca956d0df5a6` |
| `assets/demo_audio/amazing_grace_synth.truth.json` | Synthesizer truth, used for scoring only | `1072dedc12eb0ebe9a49495e6cc69e8f7de5436e29e5ab43ced9203356a75eaa` |
| `pipeline/synth_demo_voice.py` | Demo voice synthesizer | `a28412042117305c94dc3096b27dbc692fa3d293147d15fcc457e40ba5e63548` |
| `pipeline/analyze.py` | Analysis | `a0984446ee163e4f670dcef6624bf9d0a4a447a34d85a10499fe72db6047a240` |
| `pipeline/evaluate.py` | Scoring | `e777a1ab35f21813a55c0e4351d476ef85aea0c1ae8751a2c96371ce2e6212a0` |
| `pipeline/build_page.py` | Page builder | `d0827b1065701ebb3f9340c1ac415d33d8724524e42fb02f3e8c0ea98e7c4332` |
| `render/dashboard.js` | Shared renderer | `f06ab77bc05ba16665c9f780264305f85530fe4860e254369f3d4183be930093` |
| `render/render_video.js` | Video exporter | `b5e0632ed3327cfbd719a96cc971a7d81666bff4d44baa48b105c74d204c1a11` |
| `run_pipeline.sh` | Pipeline entry point | `a750b42c66274f521df65c62adc555da34b1a32999d0705b5f25e59ee405edd5` |
| `docs/howto.md` | How-to | `f82701a13c5f0a9f20e0097850b8483e413ed3cdf0ba3070bb66fb033a4ccbac` |
| `notes/METHOD.md` | Pitch method and what is illustrative | `c60c509d4c39e61ea033cca77834b88ee262c493c627a13f1a39bc9e784146d6` |
| `notes/DEMO_AUDIO.md` | Audio source and license | `1b80ace8913c021d27c4bf28aaa242caaaab7b4aafb8fc408607ebb2ee1981f8` |

## Demo audio source

Newly synthesized by `pipeline/synth_demo_voice.py`: a formant-synthesized adult voice singing the first verse of "Amazing Grace" (text 1779, tune 1829, both public domain). No recording of a person was used. The reference video's soundtrack was never decoded or used. Details: `notes/DEMO_AUDIO.md`.

## Claims this material supports

- The pipeline takes a clip and lyric text and produces a synced dashboard video and a player page.
- Pitch and note blocks are extracted from the audio with pYIN and rule-based segmentation.
- On the demo clip, against the synthesizer's own truth: median pitch error 6.2 cents, RMS 20.24 cents, 38 of 38 notes detected, 35 of 38 matched within 120 ms of onset with correct pitch.
- The dashboard follows the reference layout: three columns, fixed playhead over a scrolling roll, English labels, and a disclaimer in the header.

## Claims this material does not support

- Articulation, airflow, lung volume and the glottis view are illustrative rules. They are not measured, medical or studio data.
- The scores do not show accuracy on real singing. The clip is synthetic, and the thresholds and octave fixes were adjusted on this same clip.
- Syllables and phones are lyric text aligned to notes, not recognized from audio. Phone timing was not scored.

## Limitations

- Tested on one synthetic clip only.
- The voice is a robotic formant synthesis. Nobody has listened to it yet; it was checked by measurements and images only.
- Video output was checked by viewing frames extracted from the MP4, not by watching it play with sound.
- The player page was exercised only by running its scripts in Node with a stub DOM. It has not been played in a real browser.
- The melody arrangement was written from memory and may differ from published settings.
- `notes/reference/frames/` holds 7 frames (target-01, 08, 16, 24, 32, 40, 46), not the 46 the brief's range suggests. Only frames 01, 24 and 40 were viewed.
- `results/preview/`, `results/preview2/` and `results/qc/` are working leftovers, not deliverables. `results/qc/chrome` is a 105 MB browser profile from a failed screenshot attempt and can be deleted.
