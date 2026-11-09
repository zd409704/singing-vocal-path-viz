# What the current synthesizers lack

Model: `notes/VOICE-CONSTITUTION.md`. Earlier numbers: `notes/COMPARISON-chimera.md`, `results/chimera/comparison.json`. New numbers: `results/voice_upgrade/comparison.json`, from `tools/measure_voice_upgrade.py`.

**The implementing agent cannot hear audio.** Statements about perceived humanity are predictions from the model. Earlier versions measured well and were still rejected by ear (`notes/OWNER-LISTEN-quality-fix.md`).

## A correction to the earlier sibilant numbers

`tools/compare_chimera.py` searches for the sibilant peak from 150 ms before to 200 ms after the phone start, using the **sealed** synth's phone times for CHIMERA. Two diagnostic renders (`results/voice_upgrade/diag/`) show that this caught neighbouring vowels:

- With all CHIMERA noise sources set to zero, that metric barely moved: median −25.3 dB stock, −25.2 dB without noise.
- Measured strictly inside the phones that CHIMERA's planner placed, /s/ falls from about −28 dB (one token −37 dB) to between −58 and −76 dB with noise off. So /s/ is noise-driven, and the true window does isolate it.
- CHIMERA's planned /s/ lasts **96 ms**. The "249 ms" figure in `notes/COMPARISON-chimera.md` was not the length of the sibilant.

`notes/COMPARISON-chimera.md` is left unchanged as instructed. Use the table below for sibilants. The same windowing caveat applies to that note's formant-synth sibilant lengths, though the formant synth's phones are its own.

## Measurements, each voice in its own phone windows

Levels are dB re each file's 95th-percentile frame RMS unless stated.

| Measure | Sealed | v3 | CHIMERA first | Upstream singer (other songs) |
| --- | --- | --- | --- | --- |
| /s/ and /ʃ/ peak, 4 to 12 kHz | −27.3 | −46.2 | −27.9 | not available |
| /s/ and /ʃ/ centroid (Hz) | 6795 | 5154 | 5777 | not available |
| /s/ and /ʃ/ length (ms) | 140 | 78 | 96 | not available |
| Long-vowel level, 4 to 12 kHz | −56.8 | −56.1 | −26.7 | not available |
| Long-vowel flatness, 4 to 12 kHz | 0.000 | 0.000 | 0.034 | not available |
| Band 4 to 8 kHz re 0 to 8 kHz total | −49.5 | −49.3 | −22.7 | −24.8 |
| Band 2 to 4 kHz | −22.7 | −22.4 | −16.0 | −18.4 |
| Band 1 to 2 kHz | −16.2 | −16.6 | −14.9 | −15.1 |
| Band 0.5 to 1 kHz | −1.9 | −2.0 | −3.1 | −6.7 |
| Band 0 to 0.5 kHz | −9.5 | −9.5 | −12.2 | −4.0 |
| H1−H2, notes ≤ D4 (dB) | −1.9 | −2.0 | −6.6 | +4.0 (≤ C4) |
| H1−H2, notes ≥ G4 (dB) | −6.1 | −1.5 | −7.4 | +0.1 (≥ G4) |
| Aperiodicity (this tool's YIN) | 0.0021 | 0.0018 | 0.0037 | 0.005 (upstream's YIN) |
| Vibrato share of long notes | 0.70 | 0.87 | 0.83 | 0.64 |
| Vibrato depth (peak cents) | 28.8 | 24.4 | 31.6 | 39 |
| Vibrato rate (Hz) | 5.55 | 5.25 | 5.94 | 6.1 |
| Level in rests | −51 | −60 | −132 | not available |

Singer figures are upstream's song-level medians. Tools, dataset and repertoire differ, so read them as direction only. Upstream's H1−H2 bins are not the same as these (≤ D4 here is the lowest notes this score has).

## In-house formant synth

| Gap | Evidence | Predicted effect |
| --- | --- | --- |
| **No lips and no closure physics.** Labials are formant and gain moves. | `pipeline/synth_demo_voice.py`: `B` is voice gain 0.1 and a noise burst; `M` keeps voice gain 0.85 with a nasal mix. No articulator, pressure build-up or release event. | The labial "release rise" (16.6 dB sealed, 23.9 dB v3) in these windows is largely the vowel coming back. `notes/COMPARISON-chimera.md` found a median rise of +1.2 dB just after the quietest frame, so no real transient. Consonants likely read as dips in a continuous tone. Weakens both humanity and articulation habits. |
| **Sibilants are added noise, not a jet in a tract.** | Fixed gain, centre and bandwidth per phone. v1 /s/ centred at 6.8 kHz with no voice under it. v3 reduced level by about 19 dB and reshaped it. | The owner heard leaky hiss on v2, whose fix was mainly lower gain. v3 risks a lisp (`LISTEN-quality-fix-v3.md`). Level changes do not address the structure. |
| **Nothing above about 4 kHz in vowels.** | Long-vowel 4 to 12 kHz at −56.8 dB and flatness 0.000; band 4 to 8 kHz is −49.5 against upstream's singer at −24.8. | With no noise or upper harmonics in the voice, consonant noise stands alone in that band. Plausible reason why /s/ reads as a separate leak at any level: about 29 dB above the vowels on the sealed demo. |
| **Breath is a noise patch.** | A gated, filtered noise in rests at a fixed level. No lung model; voice and breath are unrelated. | The owner heard unnatural breath and phrasing on v2. |
| **Fixed pulse.** | Pulse parameters are constants. | Voice quality does not change with pitch or level, so the source's habits are not those of a person. |
| **Vibrato and scoop are independent per note.** | Random rate and depth on notes over 0.55 s. | Variation without a singer's structure. |

## CHIMERA first version

| Gap | Evidence | Predicted effect |
| --- | --- | --- |
| Lips are **present**, not a gap. | Six labials reach contact, 70 to 100 ms; level while shut −16.7 to −34.7 dB; release rises up to +62.3 dB (`lip_contacts`). | The strongest human cue this engine has over the formant synth. |
| **Extra high-band energy inside vowels is harmonic, from the glottal pulse. It is not aspiration.** | Diagnostic: with the glottal noise source off, long-vowel 4 to 12 kHz stays −26.8 dB and flatness only drops from 0.035 to 0.028. Softening the source moves it: brightness 0 gives −32.2 dB, tension 0.35 gives −30.9 dB, both give −35.0 dB. | `notes/COMPARISON-chimera.md` raised aspiration as a possibility; this rules out aspiration as the main cause. The likely perceptual risk is a pressed, buzzy or edgy voice. Band 4 to 8 kHz is −22.7 here, which is close to upstream's singer at −24.8, so this song on a female body is less far off than upstream's own 7.5 dB average; band 2 to 4 kHz is 2.4 dB high. |
| **Source does not track pitch like a singer.** | H1−H2 is −6.6 low and −7.4 high here, against upstream's singer at +4.0 and +0.1. Upstream reports its synth's H1−H2 rising with pitch by 14 dB where the singer's falls about 4 dB, and calls the source too pressed. | The strongest measured source gap. Constant, pressed-sounding phonation. |
| **Rests are digital silence with no inhale.** | −132 dB in all three rests. The score plan has no inspiration gesture; the only breath gesture is exhalation. | Phrases start and stop from nothing. Predicted to sound cut off, and there is no breath habit. |
| **Dry output.** | No room or microphone in the CLI render. | Silence at phrase ends is abrupt. This is a recording-chain gap more than a voice gap. |
| **Uniform vibrato.** | Same depth (35 cents) on every vowel over 0.3 s, one rate. Share 0.83, depth 31.6. | Upstream's singer uses it on about two thirds of notes, deeper and slightly faster. |
| **Flat phrase dynamics.** | One breath gesture at constant pressure per phrase. | No arc, no phrase-final decay shaped by the singer. |
| /z/ is mostly voicing here. | With noise off, /z/ HF peak changes by only 1 to 4 dB (−31.1 to −35.0 at 3.8 s). | Weak frication on /z/. Lower priority. |
| No singer-specific consonant timing. | Sung consonants are 0.8 of spoken length, all alike. /s/ 96 ms. | Fricative length may hold up the line. Whether it is too long cannot be judged by measurement alone. |

## What the gaps imply

**Humanity.** The formant synth lacks a body: no closures, no airflow, no link between breath and voice. These cannot be added as gain changes. CHIMERA has the body but no performer: no inhale, a constant source, a uniform vibrato, a flat phrase.

**Voiceprint.** Neither engine holds a deliberate identity. The formant synth's long-term spectrum has almost nothing above 4 kHz in voiced sound, which an individual's voice would have. CHIMERA has anatomy from a preset, and its source habits are the default.

**Path.** The missing parts of CHIMERA (performance and source coupling) are additive to an airway that already exists. The formant synth would need a new airway and lips, which is what CHIMERA already is. The upgrade should therefore be a **local CHIMERA patch**.
