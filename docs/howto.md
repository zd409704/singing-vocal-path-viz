# VOCAL PATH: how to run

Turns a short a cappella clip into a synced three-column dashboard video and a local player page.

## Setup (once)

```bash
python3 -m venv .venv
.venv/bin/pip install numpy scipy soundfile librosa numba
(cd render && npm install)
```

`ffmpeg` must be on the PATH. Video export uses IBM Plex fonts from the system font path set at the top of `render/render_video.js`, and falls back to a default font if they are missing.

## Run

Regenerate the demo clip, analyze it, score the analysis, then render:

```bash
./run_pipeline.sh
```

Use your own audio:

```bash
./run_pipeline.sh path/to/clip.wav path/to/lyrics.json
```

The lyrics file is optional. Without it, each note gets a coarse vowel guess from LPC formants and the note name as its pronunciation line. That guess is unreliable at high pitch.

Lyrics format (syllables in sung order, with no timing; `notes` is how many detected notes the syllable covers):

```json
{"title": "Song", "subtitle": "SONG · SINGER",
 "syllables": [{"grapheme": "ma", "pron": "may", "phones": ["M", "EY"], "notes": 3}]}
```

If the note count from the lyrics differs from the number of detected notes, the analysis prints a warning and spreads syllables proportionally, so the lyric timing is only approximate.

Before using anyone else's recording, check that you have the right to use it.

## Output

| File | What it is |
| --- | --- |
| `results/vocal_path_demo.mp4` | 1920x1080, 30 fps dashboard with audio |
| `results/vocal_path_demo.html` | Local player; keep `vocal_path_audio.m4a` next to it |
| `results/analysis.json` | Pitch, notes, phones and illustrative tracks at 100 Hz |
| `results/analysis_metrics.json` | Pitch and note scores against the synthesizer's truth (demo clip only) |

## Code

| File | Job |
| --- | --- |
| `pipeline/synth_demo_voice.py` | Creates the demo clip |
| `pipeline/analyze.py` | pYIN pitch, notes, lyric alignment, illustrative mapping |
| `pipeline/evaluate.py` | Scores the analysis against synthesizer truth |
| `render/dashboard.js` | Canvas renderer shared by the video and the page |
| `render/render_video.js` | Exports frames to ffmpeg; `--still 9.5,19` writes PNG previews |
| `pipeline/build_page.py` | Builds the single-file player page |

Method and limits: `notes/METHOD.md`. Audio source and license: `notes/DEMO_AUDIO.md`.
