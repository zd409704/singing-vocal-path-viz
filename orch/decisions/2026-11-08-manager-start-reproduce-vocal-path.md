# Manager START — reproduce singing vocal-path visualization

Date: 2026-11-08 Asia/Shanghai
From: Claude Manager
To: Claude 4

## Context
Owner asked Claude 4 to start Claude Code, create a new program, and reproduce the visual effect in this public post:

https://x.com/slashui/status/2119421849134305644

The post shows an a cappella singing recording turned into a synced dashboard video. A later quote in the same thread points at an earlier neon midsagittal vocal-tract style; the target for this packet is the dashboard in the linked post itself, not that earlier style.

A visual reference copy of the source video and sampled frames live under notes/reference/. Use them only to match layout and motion. Do not extract or reuse the source soundtrack as the demo audio (it is a child singing). Do not redistribute that audio.

## What to reproduce
A dark dashboard, roughly three columns, synced to a singing recording:

1. Left: full-body wireframe side view with lungs, airway, and animated airflow; a lung-volume readout.
2. Center top: midsagittal cut of the oral cavity and vocal tract (nasal cavity, soft palate / velum, hard palate, tongue, jaw, lips, pharynx, glottis) with illustrated airflow.
3. Center bottom: current syllable or phone (grapheme plus pronunciation), current pitch name and cents offset, sliders or bars for tongue height, tongue backness, tongue tip, jaw opening, lip rounding, velum opening, and airflow, plus a small glottis schematic.
4. Right: piano-roll pitch chart (about G3 to D5), note blocks for detected sung notes, a live pitch trace that can wobble and show vibrato, color for recorded notes / stable tracking / pitch deviation, a breath or voicing energy strip under the roll, and a phoneme timeline. A playhead and timestamp scan left to right.

The source UI itself states that notes come from the recording and that articulation and airflow are illustrative, not physically measured. Keep that honesty: extract pitch (and, if feasible, note segments and phones) from audio; drive the tract and breath animation from a clearly labeled illustrative mapping (for example from estimated phones, pitch, and energy). Do not claim medical or studio-measured articulation.

English labels are required in all code, comments, UI chrome, and notes (same layout, equivalent wording). Example title already present in the source in Latin letters: VOCAL PATH.

## START
1) Create and own this new program at `/srv/claude/research/singing-vocal-path-viz/`. Start Claude Code for the work.
2) Build a runnable pipeline: singing audio in, analysis, then a synced visualization video out (a playable local page is welcome in addition to the video).
3) Demo audio must be a separately sourced short a cappella clip: public-domain singing, or a newly synthesized or newly recorded adult clip that this program is allowed to use. Do not use the reference post audio. Do not use a copyrighted commercial song as the demo track.
4) Land a first visible demo rather than a perfect physiological model. Honest illustrative articulation is in scope; a full biomechanical vocal-tract solver is not required for this packet.
5) Writes stay under `/srv/claude/research/singing-vocal-path-viz/`. Do not write other programs STATUS files. Do not copy commercial product or company names into this program files or prompts.
6) Deliverables: runnable code plus a short how-to; at least one demo video under `results/` that shows the dashboard following a singing clip (pitch trace visibly tracking the voice, tract and breath moving with the performance); numbers or a short note on how pitch was extracted and what is illustrative; `STATUS.md` update; `notes/MATERIAL.md` when sealed.

## Priority
Owner asked for a new project that reproduces the linked post effect. Land a watchable demo.

