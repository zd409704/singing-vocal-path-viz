# How a human singing voice and a voiceprint are constituted

Decision: `orch/decisions/2026-11-09-manager-start-voice-upgrade.md`.

**Sources of numbers.** Every number here comes from this program's code or measurements, or from CHIMERA's upstream docs and code, and is labelled. The physiology is established voice science stated qualitatively, from general knowledge; no human recording was measured for this note. The only real-singer figures are upstream's, from `third_party/chimera-vocal-synth/docs/csd-comparison.md` (one professional female singer, Children's Song Dataset, different songs from ours). They were not re-run here. Upstream's own caveat applies: they are directions, not targets for every voice.

The implementing agent cannot hear audio.

## 1. Source: lungs and vocal folds

Lung pressure drives air through the adducted folds, which open and close once per cycle. Three things matter.

- **Pulse shape sets spectral tilt.** How abruptly the folds close decides how much energy reaches the upper harmonics. Open quotient and closing speed are voice-quality controls, usually summarised by H1−H2 (first minus second harmonic): high reads breathy or lax, low reads pressed.
- **Source settings move with pitch and loudness.** In a real singer they are not constants. Upstream's singer has H1−H2 of +4.0 dB on notes at or below C4 and +0.1 dB on notes at or above G4 (`csd-comparison.md`).
- **Cycle-to-cycle irregularity is small but present.** Jitter (period) and shimmer (amplitude) exist in healthy voices. Upstream's singer has YIN aperiodicity 0.005.

In this program:

| | Source model |
| --- | --- |
| Formant synth | Fixed pulse shape (`open_rise` 0.40, `open_fall` 0.18), period jitter 0.004, amplitude jitter 0.02 (`pipeline/synth_demo_voice.py`). The pulse does not change with pitch or level. |
| CHIMERA | Parametric glottal **area**; flow comes from the airway solver, so source and tract interact (`sources/glottis.rs`). Open quotient, skew and closure sharpness follow tension and effort, and effort follows applied pressure (`voice/human_voice.rs`). |

## 2. Filter: the vocal tract

The tract from glottis to lips is a resonator whose shape sets the formants. F1 and F2 mainly carry vowel identity. Higher formants depend more on individual anatomy (section 8). At sung pitches, harmonics are widely spaced and formants are only sampled at them; singers adjust the tract, for example keeping F1 near or above f0 on open vowels at high pitch. The sealed synth has a coarse version of this: `f[0] = max(f[0], min(f0 * 1.08, 950))`.

The score here is C4 to C5 in sounding pitch class, with 38 sung notes (`notes/COMPARISON-chimera.md`). Upstream notes that at C4 to C6 LPC formants snap to harmonics, which is why this program's new measurements use band levels rather than formant tracks.

## 3. Articulators: tongue, jaw, velum, lips

Speech sounds are made by moving physical structures that have mass and overlap in time.

- **Tongue and jaw** shape the oral cavity and form alveolar and velar constrictions. Because gestures overlap, a consonant's realisation depends on its neighbouring vowels (coarticulation).
- **Velum** opens the nasal branch. Sound leaves through the nose during /m n ŋ/ while the mouth is closed, and nasalisation spreads onto neighbouring vowels.
- **Lips** close completely for /m b p/. During /m/, the voice continues through the nose. During /b p/, pressure builds behind the closure, and the release is a transient: a brief acoustic event that no steady filter setting can produce. /f v/ add a labiodental constriction, and rounding lengthens the tract and lowers its resonances.

CHIMERA models these as articulators with a branched airway. Its articulator track shows every labial in this song reaching contact (`results/chimera/comparison.json`, `lip_contacts`; aperture at or below 0). The formant synth has no articulators; labials are moves in formant targets and gain.

## 4. Lip radiation

Sound leaving the mouth is approximately the time derivative of the flow at the lips, which boosts high frequencies. It also means the mouth opening and body scale affect level and brightness. CHIMERA computes radiated flow from its airway (`airway/network.rs`, `radiated_flow`) with a body-scale gain. The formant synth imitates differentiation inside the source (`dg`, then `tilt`).

## 5. Aspiration and turbulence

Air through a narrow opening becomes turbulent and makes noise.

- **Aspiration** is noise at the glottis. It is present to some degree in voiced sound and is strongest in /h/ and after voiceless stops. Because it depends on flow, it is modulated by the glottal cycle, so it fuses with the voice instead of sitting beside it.
- **Frication** is noise at a supraglottal constriction, filtered by the cavity in front of it. /s/ and /ʃ/ also use a jet striking the teeth, which makes them far stronger and higher than /f/. Sibilants are shaped by the tract, including the following vowel's lip and tongue posture.

CHIMERA derives noise amplitude from Reynolds number (`compute_noise`) at the glottis, the narrowest constriction and the teeth. The formant synth uses band-filtered noise with a fixed gain and centre per consonant.

## 6. Pitch and vibrato

A sung note is a trajectory, not a value: onset approach, settling, vibrato and slow drift. Vibrato tends to bloom after the note starts and varies from note to note. Upstream's singer: vibrato on 64% of long notes, depth 39 peak cents, rate 6.1 Hz (`csd-comparison.md`). Stock CHIMERA on that dataset: 100% of notes, 35 cents, 5.5 Hz.

## 7. Phrasing and breath

Singing is organised by breath. A phrase is one exhalation. Pressure is shaped across it, the voice decays or lifts at phrase ends rather than switching off, and an inhale precedes the next phrase. Level and voice quality are linked, because harder drive changes the pulse as well as the amplitude. Rests in a real recording also contain the room and the inhale.

For this program: the sealed score has line-end rests after "sound", "me" and "found". `notes/LISTEN-quality-fix-v3.md` records that removing rests leaves a 19.6 s stretch with no breath, which no singer does. That is why this packet keeps real breaths and changes what happens inside them.

## 8. What identifies a speaker

A voiceprint is a set of long-term tendencies that persist across different words, as opposed to the words themselves.

- **Anatomy:** vocal tract length and shape (overall formant scale, and especially the higher formants and the region above about the third formant), fold size (pitch range), and nasal cavity geometry.
- **Source habits:** typical open quotient and spectral tilt, chink leakage, typical aperiodicity, and how these change with pitch and loudness.
- **Motor habits:** consonant timing, coarticulation style, vibrato rate and shape, attack style, breath placement.
- **Long-term summaries:** the long-term average spectrum, and the pitch distribution.

Speaker-recognition systems use statistical summaries of short-term spectra over time, which is why consistency across a whole performance matters as much as any single frame.

Implication: a voice with an identity needs one fixed set of anatomy and habits held through the song, plus *structured* variation around them. Independent randomness on each note gives neither.

Neither current engine has a named identity. The formant synth has published-average female targets (`notes/DEMO_AUDIO.md`). CHIMERA has a body preset. This packet does not model or imitate any real person, and any identity built here is fictional.

## 9. What this model predicts a synthesizer needs

| Layer | Required behaviour |
| --- | --- |
| Source | Pulse and tilt that follow pitch and pressure; small irregularity |
| Filter | Vowel and individual resonances, fixed anatomy |
| Articulators | Real closures and overlapping gestures |
| Noise | Flow-derived, shaped by the tract, fused with voicing |
| Pitch | Note trajectories; vibrato that varies note to note |
| Breath | Pressure shape across phrases, inhale in rests, phrase-final decay |
| Identity | One consistent body and set of habits |
