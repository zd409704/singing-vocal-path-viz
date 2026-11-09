# Synthesizer algorithm root fix

Human lead: Peter. Decision: `orch/decisions/2026-11-09-manager-start-synth-algo-rootfix.md`. Prior findings: `notes/TWO-TIGERS-PRONUNCIATION.md`.

**The implementing agent cannot hear audio.** This note reports code changes and measurements. It does not claim a very good voice and does not claim any owner-heard mismatch is fixed. Owner ear remains the acceptance gate.

## How the rules are switched on

The rules are general and carry no song or token conditions. They are on when a score sets `"phonologyRules": true`, which becomes `SongOptions.rules` and `PlanOptions.rules`. The switch exists only so older score files keep rendering as they did. Through the new binary, the old Two Tigers score reproduced `results/nursery/raw/two_tigers.wav` byte for byte. The speech and live-note paths leave it off, so rule 1 is not yet active for spoken text (see limits).

## The nine rules

Engine paths are under `third_party/chimera-upgrade/crates/`. `crates/chimera/tests/sing_rules.rs` has 8 tests covering each engine rule on patterns not taken from the reported lyrics where possible.

| # | Rule | Where | Why it is not a result patch |
| --- | --- | --- | --- |
| 1 | An onset voiceless stop looks through approximants and laterals to a vowel and is aspirated, unless after /s/. Coda stops do not use the lookahead. | `planner.rs`, `vowel_through_glides`; sung path marks codas with `Segment.coda` | Keys on manner and syllable position only: /kw tw pl/ and so on |
| 2 | Each inhale, ramp included, ends 20 ms before the phrase's first scheduled segment. A `--plan-only` engine pass supplies those times. | `tools/make_upgrade_notes.py`, `first_onsets` and `inhales`, shared by both planners; `render.rs --plan-only` | Uses the engine's own schedule for any score |
| 3 | Per-render `"lexicon"` (word to phones) wins over the dictionary. Two Tigers builds it from pinyin spelling rules (`-ang` to AA NG, `zh-` to the new affricate). | `english.rs`, `add_lexicon`; `render.rs`; `make_nursery_notes.py`, `pinyin_lexicon` | Any score can request phones spelling cannot reach. The spelling rules fire on the syllable shape, and already cover both `zhi` and `zhen` |
| 4 | A tongue-tip gesture after /ŋ/ starts after the velar release and velum closure. The onset grows by the delay so its closure is not shortened. | `planner.rs`, `tip_delay_after_velar_nasal`; `sing.rs`, `apply_rules` | Any /ŋ/ plus any consonant with a tip gesture |
| 5 | A phrase-final sung nasal holds at least 130 ms, capped at 30 % of its note. | `sing.rs`, `apply_rules` | Any final nasal |
| 6 | New inventory phone /ʈʂ/: retroflex closure, /ʂ/ release, flagged never aspirated. Requested as `TSR` through the lexicon. | `inventory.rs`, `english.rs`, `ipa.rs`, `syllables.rs` | Inventory item; no audio splice and no /tʃ/ stand-in |
| 7 | Coda /l/ becomes dark /ɫ/ on the sung path. | `sing.rs`, `apply_rules` | Any coda /l/. Flapping was not added: it is not a coda rule |
| 8 | A word-final stop before a vowel-initial word holds 1.5 times as long, then a 35 ms glottal onset separates its release from the next vowel. | `sing.rs`, `apply_rules` | Any such boundary. The room mix was not changed |
| 9 | A word-initial /s/ after a coda consonant skips the extra fricative scale. Other fricatives keep 0.75. | `sing.rs`, `apply_rules` | Any word-initial /s/ after a coda |

No notes or WAV samples were hand-edited, and no burst or sibilant was inserted in a post-process.

## Measurements at the eight loci

From `tools/measure_algo_rootfix.py`, written to `results/algo/loci_measurements.json`. Levels are dB re the following vowel, in the dry engine output unless marked. "Voicing onset" is ms after the planned release until 5 frames are periodic and within 15 dB of the local vowel peak. Values are the first pass, or a range across passes. Before is the untouched `*_upgrade` render; after is `*_algo`.

| Locus | Measure | Before | After |
| --- | --- | --- | --- |
| liang | Scheduled nucleus | æ, 432 ms | ɑ, 361 ms |
| liang | Tongue tip during /ŋ/ (ttY max) | 9.87 | 6.89 |
| liang | 100 Hz frames with tip at contact and velum open | 7 | 0 |
| kuai | Voicing onset | 28 ms | 64 ms |
| kuai | Release peak, 2.5-8 kHz | −13.1 dB | −21.9 dB (lower) |
| jing | /ŋ/ length | 64 ms | 130 ms |
| jing | Tip stays down (ttY max) | 7.24 | 7.24 |
| zhen | Scheduled onset | dʒ, voiced | ʈʂ, voiceless |
| zhen | Voicing onset | none measurable before the vowel (−10) | 24 to 26 ms |
| zhen | 4-12 kHz frication peak | 3.5, 2.6 dB | −0.1, 0.6 dB (lower) |
| zhen | Inhale end to first segment | overlap 64 ms | clear 20 ms |
| twin, passes 1 and 3 | Voicing onset | 32, 34 ms | 66, 66 ms |
| twin, passes 1 and 3 | Release peak, 2.5-8 kHz | −19.4, −19.3 dB | −11.2, −10.2 dB |
| twin, after /l/ | Voicing onset | 26, 28 ms | 64, 64 ms |
| twin, after /l/ | Closure minimum | −40.7, −37.8 dB | −42.9, −43.0 dB |
| kle | Coda phone, tbX | l, 2.98-3.10 | ɫ, 1.94-2.17 |
| kle | /k/ (burst, voicing onset) | 3.7 dB, 64 ms | 3.7 dB, 64 ms (unchanged) |
| up | /p/ closure length | 68 ms | 102 ms |
| up | Next segment | ə, directly | ʔ, 35 ms, then ə |
| up | Finished closure minimum | −21.1 dB | −27.5 dB |
| up | Release peak, 2.5-8 kHz | −23.5 dB | −26.6 dB (lower) |
| so | /s/ length | 72 ms | 96 ms |
| so | 4-12 kHz peak | 0.3 dB | −0.4 dB |

Inhale overlap, as ms clear of the phrase's first segment (negative is overlap):

| Song | Before | After |
| --- | --- | --- |
| Twinkle | −68, −32, 40, −12, −68, −32 | 20 at all six |
| Two Tigers | −56, −28, −28, −4, −4, −64, −64 | 20 at all seven |

Hiss check, all /s/ in Twinkle, length and dry 4-12 kHz peak re vowel: before 72 ms at 5.1, 0.3, 3.8, 4.4 dB. After 96 ms at 2.1, −0.4, 1.3 dB where the rule fired (`star` twice and `so`), and 72 ms at 4.4 dB in `sky`, where it did not. The peak did not rise, but those /s/ are a third longer, so whether they read as hiss is for the ear.

Regression: `amazing_grace_algo` has the same segment count against `amazing_grace_upgrade_r2` apart from one added ʔ, the same 4 inhales, the same length (43.13 s), and RMS 0.2446 against 0.2462. No video or metric evaluation was run for it.

## Evidence and guess

**Evidence:** the schedules, gesture code, levels and traces above, and passing tests (`cargo test -p chimera`, `-p chimera-cli`).

**Guess:** that any of these changes moves what a listener hears toward the intended syllable. The links between causes and the owner's reports were guesses in the prior note and remain so.

## Honest limits

- Nobody has listened. These renders are checks that the rules fire, not a quality acceptance.
- Some measures moved the wrong way or did not move. The kuai and up release peaks are lower, and zhen's frication peak is lower than the voiced dʒ it replaced. kle's /k/ is unchanged, including the weak releases on the G4 passes.
- /t/ after /l/ still seals poorly (about −43 dB dry, 14 ms below −30 dB). Dark /l/ did not help, and this closure was not one of the nine rules.
- Rule 8's glottal onset is a design choice and could sound like a hard attack. It also fired at two boundaries nobody reported (`like a`, `mond in`).
- Rule 4 takes time from the vowel before it: liang's vowel is 71 ms shorter.
- /ʈʂ/ has no calibration of its own. Only its release uses the existing /ʂ/ targets.
- Rule 1 treats any preceding /s/ as blocking aspiration, including across a word boundary, as the decision worded it.
- The rules are off for speech and live notes, and the wasm build and app were not rebuilt or tested.
- Still outside this English-phone path: Mandarin tones, alveolo-palatal consonants (j, q, x use English approximations), the apical vowel of `zhi` (still ER), and the kle vowel (still ə). jing keeps IH; the IY rhyme was not tried.
