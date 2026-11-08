# How the dashboard is driven

## Extracted from the audio

- **Pitch:** `librosa.pyin` at 22.05 kHz, frame 2048, hop 256, search range C3 to A5. Octave errors are then folded back, first per frame against a local median and then per note against neighbouring notes.
- **Notes:** voiced runs split at sustained pitch changes and at level dips on long notes; short slides between two notes are dropped. Each note takes the rounded median pitch of its middle 60%.
- **Cents offset (panel):** live pitch against the nearest semitone.
- **Trace color:** teal within 30 cents of the detected note, red beyond that.
- **Energy strip:** RMS level, normalized to the clip's 98th percentile.
- **Breath gaps:** pauses in the voiced/energy mask longer than 0.28 s.

## Given as text, not extracted

Syllables and phones come from a lyric file with no timing. They are assigned to detected notes in order, and phones are spread by fixed consonant durations. This is lyric alignment, not phone recognition from audio.

## Illustrative, not measured

These come from hand-written rules. Nothing here observes a real vocal tract.

- **Tongue height, backness and tip, jaw, lips, velum:** a per-phone target table with smoothing to suggest coarticulation, plus a rule that opens the jaw wider on higher notes.
- **Airflow:** energy scaled by a per-phone openness value.
- **Lung volume:** rises to 90% in each pause and is spent down to 30% over each phrase in proportion to loudness.
- **Glottis and vocal folds:** a slowed cartoon of voiced versus breathing states. Its motion rate is not the sung pitch.
- **Body and tract drawings:** schematic. This is not medical or studio data.

## Scores against synthesizer truth

From `results/analysis_metrics.json`, plus a breakdown run on the same data.

| Measure | Value |
| --- | --- |
| Pitch frames compared | 3715 (99.87% of voiced truth frames) |
| Median absolute pitch error | 6.2 cents |
| RMS pitch error | 20.24 cents |
| RMS away from note edges (more than 150 ms) | 9.67 cents, 2726 frames |
| Frames off by more than 50 cents | 2.72% (101 frames, all within 150 ms of a note edge) |
| Notes detected / in the score | 38 / 38 |
| Matched within 120 ms of onset | 35 of 38, all 35 with correct pitch |
| Median onset error of matched notes | 46.9 ms |

**Read these as a sanity check, not as accuracy on real singing.** The clip is synthetic and much cleaner than a phone recording. The segmentation thresholds and both octave fixes were also adjusted while looking at this same clip, so the note scores in particular are optimistic. Truth pitch and notes are read only by `evaluate.py`, never by the analysis itself.

Phone timing was not scored.

## Known limits

- The pipeline has been run on this one synthetic clip only.
- The clip is a robotic formant voice. Its sound was checked only through level and pitch measurements and images; nobody has listened to it yet.
- Segmentation can split or merge notes on real singing, which triggers proportional lyric spreading.
