# singing-vocal-path-viz

A short a cappella clip becomes a synced VOCAL PATH dashboard video: pitch tracking on a piano roll, next to an illustrated breath and vocal-tract view.

How to run: see `docs/howto.md` and `./run_pipeline.sh`.

## Demo

`results/vocal_path_demo.mp4` is a sealed 1920x1080, 30 fps, 43-second demo with audio. The voice is a newly synthesized adult formant voice singing the first verse of Amazing Grace (text 1779, tune 1829, both public domain). No recording of a person was used. Details: `notes/DEMO_AUDIO.md`.

## What is measured vs illustrative

- From the audio: pitch, note blocks, energy and breath gaps.
- From lyric text (not recognized from the sound): syllables and phones, aligned to detected notes.
- Illustrative, and labeled that way in the dashboard: tongue, jaw, lips, velum, airflow, lung volume, and the glottis view.

Articulation and airflow are not claimed as measured.

## Visual reference

The dashboard layout follows a public post used as a layout and motion reference only. That reference video and its soundtrack are not in this repository and must not be extracted or redistributed from the local research tree.

## Contents note

See `GITHUB-CONTENTS.md` for what this snapshot includes and omits.
