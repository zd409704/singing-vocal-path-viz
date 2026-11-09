//! The phonological rules behind `SongOptions::rules`, each on its general pattern.

use chimera::control::score::ControlKey;
use chimera::phonetics::Plan;
use chimera::phonetics::english::{EnglishG2P, arpabet_to_segments};
use chimera::phonetics::sing::{SongOptions, SungNote, plan_song};
use chimera::phonetics::syllables::lyrics_to_syllables;

fn g2p() -> EnglishG2P {
    let mut g = EnglishG2P::new();
    g.load_dict("twin\tT W IH1 N\ntin\tT IH1 N\nspin\tS P IH1 N\nup\tAH1 P\na\tAH0\nsing\tS IH1 NG\nto\tT UW1\nbell\tB EH1 L\nworld\tW ER1 L D\nso\tS OW1\nthe\tDH AH0\nsky\tS K AY1\nkeep\tK IY1 P\nwe\tW IY1\n");
    g
}

fn plan(lyrics: &str, rules: bool) -> Plan {
    let syl = lyrics_to_syllables(lyrics, &g2p());
    let notes: Vec<SungNote> = syl.iter().map(|s| SungNote { midi: 60.0, beats: 1.0, syl: s.clone() }).collect();
    plan_song(&notes, &SongOptions { body: "female".into(), bpm: 80.0, t0: 0.5, vibrato: 0.0, fricative_scale: 0.75, rules, ..Default::default() })
}

fn seg<'a>(p: &'a Plan, ipa: &str, n: usize) -> &'a chimera::phonetics::PlannedSegment {
    p.segments.iter().filter(|s| s.ipa == ipa).nth(n).unwrap()
}

/// Peak abduction target of the stop gesture around a segment.
fn stop_abduction(p: &Plan, ipa: &str) -> f64 {
    let s = seg(p, ipa, 0);
    p.gestures.iter().filter(|g| g.label_str() == "aspiration" && g.t0 >= s.t0 - 1e-6 && g.t0 < s.t1).map(|g| g.targets.get(ControlKey::ABDUCTION).unwrap()).next().unwrap()
}

#[test]
fn stop_plus_glide_plus_vowel_is_aspirated_unless_after_s() {
    assert_eq!(stop_abduction(&plan("twin", false), "t"), 0.22);
    assert_eq!(stop_abduction(&plan("twin", true), "t"), 0.36);
    assert_eq!(stop_abduction(&plan("tin", true), "t"), 0.36);
    assert_eq!(stop_abduction(&plan("spin", true), "p"), 0.22);
}

#[test]
fn a_coda_stop_does_not_borrow_the_next_onset() {
    // /p/ of "keep" before "we": a coda stop, so the /w/ onset does not make it aspirated
    assert_eq!(stop_abduction(&plan("keep we", true), "p"), 0.22);
}

#[test]
fn word_final_stop_before_a_vowel_stays_a_coda() {
    let (off, on) = (plan("up a", false), plan("up a", true));
    assert!(off.segments.iter().all(|s| s.ipa != "ʔ"));
    let p = seg(&on, "p", 0);
    assert!(p.t1 - p.t0 > 1.4 * (seg(&off, "p", 0).t1 - seg(&off, "p", 0).t0));
    assert_eq!(on.segments.iter().find(|s| s.t0 >= p.t1 - 1e-9).unwrap().ipa, "ʔ");
}

#[test]
fn phrase_final_nasal_is_held() {
    let plain = plan("sing", false);
    let rule = plan("sing", true);
    let d = |p: &Plan| seg(p, "ŋ", 0).t1 - seg(p, "ŋ", 0).t0;
    assert!(d(&plain) < 0.07);
    assert!((d(&rule) - 0.13).abs() < 1e-6);
}

#[test]
fn coronal_gesture_waits_for_a_velar_nasal() {
    let p = plan("sing to", true);
    let (ng, t) = (seg(&p, "ŋ", 0), seg(&p, "t", 0));
    let tip = p.gestures.iter().find(|g| g.label_str() == "t" && g.t0 >= t.t0 - 0.04 && g.targets.has(chimera::anatomy::human::ArticKey::TtY)).unwrap();
    assert!(tip.t0 - tip.ramp_in >= ng.t1 + 0.009);
    assert!(t.t1 - t.t0 > 0.1, "the segment grows by the delay");
}

#[test]
fn coda_l_is_dark_on_the_sung_path() {
    assert!(plan("bell", false).segments.iter().any(|s| s.ipa == "l"));
    let p = plan("bell", true);
    assert!(p.segments.iter().any(|s| s.ipa == "ɫ") && p.segments.iter().all(|s| s.ipa != "l"));
}

#[test]
fn word_initial_s_after_a_consonant_is_not_shortened_further() {
    let d = |p: &Plan, n| seg(p, "s", n).t1 - seg(p, "s", n).t0;
    let on = plan("world so the sky", true);
    assert!(d(&on, 0) > d(&on, 1) * 1.2, "after /d/: {}, after a vowel: {}", d(&on, 0), d(&on, 1));
    let off = plan("world so the sky", false);
    assert!((d(&off, 0) - d(&off, 1)).abs() < 1e-9);
}

#[test]
fn a_lexicon_entry_reaches_phones_spelling_cannot() {
    let mut g = g2p();
    g.add_lexicon([("zhen", "TSR AH1 N")]);
    assert_eq!(arpabet_to_segments("TSR AH1 N")[0].ipa, "ʈʂ");
    let syl = lyrics_to_syllables("zhen", &g);
    assert_eq!(syl[0].onset[0].ipa, "ʈʂ");
    let notes = vec![SungNote { midi: 60.0, beats: 1.0, syl: syl[0].clone() }];
    let p = plan_song(&notes, &SongOptions { body: "female".into(), bpm: 80.0, t0: 0.5, vibrato: 0.0, rules: true, ..Default::default() });
    assert!(p.gestures.iter().any(|g| g.label_str() == "aspiration" && g.targets.get(ControlKey::ABDUCTION) == Some(0.22)), "unaspirated");
}
