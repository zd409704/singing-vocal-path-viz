//! Versioned voice mechanisms on top of the upgraded engine (`notes/TIMBRE-STRUCTURE.md` gaps).
//! Every mechanism is off by default and the whole struct is absent from a voice unless a render
//! asks for it, so a render without `mech` is sample-identical to the upgraded baseline.
//!
//! These are physically reduced models, labelled as such in `notes/VOICE-MECHANISMS-LIMITS.md`:
//! a symmetric two-mass fold (Ishizaka-Flanagan / Steinecke-Herzel lineage), not layered tissue.

use crate::anatomy::human::ArticKey;
use crate::control::score::{Blended, ControlKey, N_CONTROL};
use crate::anatomy::human::{BodyMix, HumanBody};
use crate::math::{Rng, clamp, cos, exp, hz_to_midi, js_max, js_min, lerp, ln, pow, sin, smoothstep, sqrt};
use crate::physics::C_SOUND;
use super::human_airway::HumanAirway;
use crate::physics::CM_H2O;
use crate::sources::glottis::ParametricGlottis;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", default, deny_unknown_fields)]
pub struct MechConfig {
    /// Seeds the glottal and airway noise generators; absent keeps the upstream fixed seeds.
    pub engine_seed: Option<u32>,
    pub fold: FoldCfg,
    pub feedback: FeedbackCfg,
    pub register: RegisterCfg,
    pub source_map: SourceMapCfg,
    pub tract: TractCfg,
    pub breath: BreathCfg,
    pub anatomy: AnatomyCfg,
}

impl MechConfig {
    /// Whether any mechanism changes the audio path (a seed alone also counts).
    pub fn active(&self) -> bool {
        self.engine_seed.is_some() || self.fold.enabled || self.source_map.enabled || self.tract.enabled || self.breath.enabled || self.anatomy.enabled
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", default, deny_unknown_fields)]
pub struct FoldCfg {
    pub enabled: bool,
    /// Vibrating fold length (cm); with `lengthFromBody`, 1.4 x body scale.
    pub length_cm: f64,
    pub length_from_body: bool,
    /// Rest half-opening scale at tension 0 (cm², both masses).
    pub rest_area: f64,
    /// Stiffness grows as Q^p and mass as Q^(p-2), so f0 goes as Q at any p.
    pub stiffness_exponent: f64,
    /// Extra rest opening of the lower mass (cm²): the convergent shape the folds need to self-start.
    pub convergence_area: f64,
    /// Coupling stiffness multiplier between lower and upper mass.
    pub coupling: f64,
    /// Open-cycle damping ratio multiplier.
    pub damping: f64,
    /// Close the pitch loop: laryngeal tension trims toward the score pitch.
    pub pitch_loop: bool,
    /// Pitch-loop time constant (ms).
    pub pitch_loop_tau_ms: f64,
}

impl Default for FoldCfg {
    fn default() -> Self {
        FoldCfg { enabled: false, length_cm: 1.4, length_from_body: true, rest_area: 0.05, stiffness_exponent: 0.3, convergence_area: 0.02, coupling: 1.0, damping: 1.0, pitch_loop: true, pitch_loop_tau_ms: 80.0 }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", default, deny_unknown_fields)]
pub struct FeedbackCfg {
    pub enabled: bool,
    /// 0 = folds feel only slow (30 Hz) sub/supraglottal pressure, 1 = full acoustic pressure.
    pub gain: f64,
}

impl Default for FeedbackCfg {
    fn default() -> Self {
        FeedbackCfg { enabled: false, gain: 1.0 }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", default, deny_unknown_fields)]
pub struct RegisterCfg {
    /// Needs `fold` (register changes the fold's vibrating mass); inert without it.
    pub enabled: bool,
    /// "auto" follows pitch through the passaggio, "chest", "head", or "mix" holds `mix`.
    pub mode: String,
    pub mix: f64,
    pub passaggio_midi: f64,
    pub width_semi: f64,
    pub hysteresis_semi: f64,
    pub tau_ms: f64,
    /// 0 = no mechanical change across registers, 1 = full mass / coupling change.
    pub break_depth: f64,
    /// Passaggio shift with lung pressure (semitones per cmH2O above 9).
    pub pressure_slope: f64,
}

impl Default for RegisterCfg {
    fn default() -> Self {
        RegisterCfg { enabled: false, mode: "auto".into(), mix: 0.5, passaggio_midi: 69.0, width_semi: 2.0, hysteresis_semi: 1.5, tau_ms: 60.0, break_depth: 1.0, pressure_slope: 0.15 }
    }
}

/// A stored personal source: settings as functions of absolute pitch, the same on every song.
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", default, deny_unknown_fields)]
pub struct SourceMapCfg {
    pub enabled: bool,
    pub name: String,
    pub midi: Vec<f64>,
    pub tension: Vec<f64>,
    pub breathiness: Vec<f64>,
    pub brightness: Vec<f64>,
    /// Tension added per cmH2O of applied pressure above 9.
    pub loudness_tension: f64,
}

impl Default for SourceMapCfg {
    fn default() -> Self {
        SourceMapCfg {
            enabled: false,
            name: "personal-default-v1".into(),
            midi: vec![48.0, 55.0, 60.0, 64.0, 67.0, 72.0, 79.0],
            tension: vec![0.25, 0.30, 0.36, 0.45, 0.52, 0.65, 0.72],
            breathiness: vec![0.18, 0.15, 0.15, 0.15, 0.15, 0.17, 0.22],
            brightness: vec![0.14, 0.15, 0.16, 0.16, 0.16, 0.15, 0.12],
            loudness_tension: 0.012,
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", default, deny_unknown_fields)]
pub struct TractCfg {
    pub enabled: bool,
    /// Keep the first formant at least this factor above f0.
    pub margin: f64,
    /// Jaw opening per unit fractional F1 shortfall (template cm).
    pub jaw_gain: f64,
    pub jaw_max: f64,
    /// Lip opening per unit shortfall.
    pub lip_gain: f64,
    /// Tongue body lowering per unit shortfall (template cm); the jaw alone barely moves F1 on high vowels.
    pub tongue_gain: f64,
    /// Larynx raised (+) per semitone above `ref_midi` (cm).
    pub larynx_per_semi: f64,
    pub ref_midi: f64,
    pub tau_ms: f64,
}

impl Default for TractCfg {
    fn default() -> Self {
        TractCfg { enabled: false, margin: 1.1, jaw_gain: 1.2, jaw_max: 0.9, lip_gain: 0.6, tongue_gain: 1.2, larynx_per_semi: 0.01, ref_midi: 60.0, tau_ms: 80.0 }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", default, deny_unknown_fields)]
pub struct BreathCfg {
    pub enabled: bool,
    /// Usable air above residual volume (ml); with anatomy on, derived from body size unless > 0.
    pub vital_capacity_ml: f64,
    /// Fraction of vital capacity at the start of the render.
    pub start_fraction: f64,
    /// Largest expiratory pressure with air to spare (cmH2O).
    pub max_pressure: f64,
    /// Below this fraction of vital capacity, deliverable pressure falls to zero.
    pub reserve_fraction: f64,
    /// Seconds spent under `fatigue_below` to reach fatigue 1; recovers at the same rate above it.
    pub fatigue_s: f64,
    pub fatigue_below: f64,
    /// Multiplier on measured inward glottal flow while inhaling: the planner's inhale gesture is a
    /// small abduction, so its airway flow alone under-fills the lungs.
    pub inhale_gain: f64,
}

impl Default for BreathCfg {
    fn default() -> Self {
        BreathCfg { enabled: false, vital_capacity_ml: 3200.0, start_fraction: 0.8, max_pressure: 30.0, reserve_fraction: 0.12, fatigue_s: 4.0, fatigue_below: 0.3, inhale_gain: 7.0 }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", default, deny_unknown_fields)]
pub struct AnatomyCfg {
    pub enabled: bool,
    pub age_years: f64,
    /// "female" or "male": sets the pubertal fold-growth path and adult tract.
    pub sex: String,
    pub scale_offset: f64,
    pub pharynx_offset: f64,
    /// Overrides the developmental fold length when > 0 (cm).
    pub fold_length_cm: f64,
    /// Largest fold tension Q; caps reachable pitch at Q x natural frequency.
    pub q_max: f64,
    pub setting_jaw: f64,
    pub setting_tongue_x: f64,
    pub setting_tongue_y: f64,
    pub setting_larynx: f64,
    pub setting_lip_prot: f64,
    pub artic_speed: f64,
    /// Depth of a smooth seeded area irregularity (fraction), 0 = mean shape.
    pub perturb_depth: f64,
    pub perturb_seed: u32,
}

impl Default for AnatomyCfg {
    fn default() -> Self {
        AnatomyCfg { enabled: false, age_years: 30.0, sex: "female".into(), scale_offset: 0.0, pharynx_offset: 0.0, fold_length_cm: 0.0, q_max: 5.0, setting_jaw: 0.0, setting_tongue_x: 0.0, setting_tongue_y: 0.0, setting_larynx: 0.0, setting_lip_prot: 0.0, artic_speed: 1.0, perturb_depth: 0.0, perturb_seed: 1 }
    }
}

impl AnatomyCfg {
    /// Body mix along a child-to-adult path. A point on that path, not a measured person.
    pub fn mix(&self) -> BodyMix {
        let child = 1.0 - smoothstep(7.0, 18.0, self.age_years);
        let female = if self.sex == "male" { 0.0 } else { 1.0 - child };
        BodyMix::new(female, child)
    }

    pub fn body(&self) -> HumanBody {
        let mut b = self.mix().body();
        b.scale = js_max(0.5, b.scale + self.scale_offset);
        // the pharynx finishes growing last
        let lag = 0.04 * (1.0 - smoothstep(12.0, 18.0, self.age_years));
        b.pharynx = js_max(0.5, b.pharynx - lag + self.pharynx_offset);
        b
    }

    /// Fold length (cm): tract and folds grow on separate timing, with a male-only pubertal surge.
    pub fn fold_length(&self) -> f64 {
        if self.fold_length_cm > 0.0 {
            return self.fold_length_cm;
        }
        let adult = if self.sex == "male" { 1.55 } else { 1.0 };
        let (a, b) = if self.sex == "male" { (11.0, 17.0) } else { (8.0, 16.0) };
        lerp(0.7, adult, smoothstep(a, b, self.age_years))
    }

    pub fn vital_capacity_ml(&self) -> f64 {
        let adult = if self.sex == "male" { 4500.0 } else { 3200.0 };
        let adult_scale = if self.sex == "male" { 1.0 } else { 0.9 };
        let r = self.body().scale / adult_scale;
        adult * r * r * r
    }
}

// Ishizaka-Flanagan values at length 1.4 cm, cgs (g, dyn/cm).
const M1: f64 = 0.125;
const M2: f64 = 0.025;
const K1: f64 = 80000.0;
const K2: f64 = 8000.0;
const KC: f64 = 25000.0;
const D1: f64 = 0.25;
const D2: f64 = 0.05;
const ZETA1: f64 = 0.1;
const ZETA2: f64 = 0.6;
const ZETA_CONTACT: f64 = 1.0;
const F_REF: f64 = 128.0;

/// Control-rate drive for the fold.
#[derive(Clone, Copy, Debug, Default)]
pub struct FoldDrive {
    pub tension: f64,
    pub brightness: f64,
    pub f0_target: f64,
}

#[derive(Clone, Debug)]
pub struct Mech {
    pub cfg: MechConfig,
    pub trace: Option<Vec<[f64; TRACE_COLS]>>,
    fs: f64,
    fold_len: f64,
    x1: f64,
    v1: f64,
    x2: f64,
    v2: f64,
    m1: f64,
    m2: f64,
    k1: f64,
    k2: f64,
    kc: f64,
    r1: f64,
    r2: f64,
    r1c: f64,
    r2c: f64,
    c1: f64,
    c2: f64,
    d1: f64,
    d2: f64,
    a0: f64,
    a01: f64,
    trim: f64,
    q: f64,
    fb: f64,
    ps_sm: f64,
    pe_sm: f64,
    p_coef: f64,
    env_hi: f64,
    env_lo: f64,
    prev: f64,
    since: f64,
    last_cross: f64,
    pub f0_meas: f64,
    voiced_count: f64,
    pub drive: FoldDrive,
    /// register state 0 (chest) .. 1 (head)
    pub register: f64,
    p_cmh2o: f64,
    f1_est: f64,
    jaw_delta: f64,
    lip_delta: f64,
    f1_counter: u32,
    /// usable air left (cm³)
    pub volume: f64,
    vital: f64,
    pub fatigue: f64,
    pub flow_acc: f64,
    flow_n: f64,
    jit: f64,
    rng: Rng,
    trace_counter: f64,
}

pub const TRACE_COLS: usize = 14;
pub const TRACE_NAMES: [&str; TRACE_COLS] = ["t", "f0Target", "f0Meas", "voicing", "q", "a0", "pLung", "tension", "register", "f1Est", "jawDelta", "brightness", "lungFraction", "fatigue"];
pub const TRACE_DT: f64 = 0.01;

impl Mech {
    pub fn new(cfg: MechConfig, fs: f64, body_scale: f64) -> Self {
        let fold_len = if cfg.anatomy.enabled {
            cfg.anatomy.fold_length()
        } else if cfg.fold.length_from_body {
            1.4 * body_scale
        } else {
            cfg.fold.length_cm
        };
        let vital = if cfg.anatomy.enabled { cfg.anatomy.vital_capacity_ml() } else { cfg.breath.vital_capacity_ml };
        let volume = vital * clamp(cfg.breath.start_fraction, 0.0, 1.0);
        let rng = Rng::new(cfg.engine_seed.unwrap_or(777).wrapping_add(91));
        let fb = if cfg.feedback.enabled { clamp(cfg.feedback.gain, 0.0, 1.0) } else { 0.0 };
        Mech {
            trace: None,
            fs,
            fold_len,
            x1: 0.0,
            v1: 5.0,
            x2: 0.0,
            v2: 0.0,
            m1: M1,
            m2: M2,
            k1: K1,
            k2: K2,
            kc: KC,
            r1: 0.0,
            r2: 0.0,
            r1c: 0.0,
            r2c: 0.0,
            c1: 3.0 * K1,
            c2: 3.0 * K2,
            d1: D1,
            d2: D2,
            a0: cfg.fold.rest_area,
            a01: cfg.fold.rest_area,
            trim: 0.0,
            q: 1.0,
            fb,
            ps_sm: 0.0,
            pe_sm: 0.0,
            p_coef: 1.0 - exp(-core::f64::consts::TAU * 30.0 / fs),
            env_hi: 0.0,
            env_lo: 0.0,
            prev: 0.0,
            since: 0.0,
            last_cross: -1.0,
            f0_meas: 0.0,
            voiced_count: 0.0,
            drive: FoldDrive { tension: 0.5, brightness: 0.25, f0_target: 110.0 },
            register: 0.0,
            p_cmh2o: 0.0,
            f1_est: 0.0,
            jaw_delta: 0.0,
            lip_delta: 0.0,
            f1_counter: 0,
            volume,
            vital,
            fatigue: 0.0,
            flow_acc: 0.0,
            flow_n: 0.0,
            jit: 1.0,
            rng,
            trace_counter: 0.0,
            cfg,
        }
    }

    /// Fold natural frequency at Q=1, scaling with 1/length.
    fn f_natural(&self) -> f64 {
        F_REF * 1.4 / self.fold_len
    }

    /// Control-rate: physical parameters from tension, pitch target and abduction.
    pub fn fold_control(&mut self, g: &crate::sources::glottis::GlottisParams) {
        let d = self.drive;
        let qff = d.f0_target / self.f_natural();
        let q_cap = if self.cfg.anatomy.enabled { self.cfg.anatomy.q_max } else { 8.0 };
        self.q = clamp(qff * exp(self.trim) * self.jit, 0.2, q_cap);
        let p = self.cfg.fold.stiffness_exponent;
        let (qk, qm) = (pow(self.q, p), pow(self.q, p - 2.0));
        let l = self.fold_len / 1.4;
        // mass goes as length squared at fixed stiffness, keeping f0 ∝ 1/length; stiffness scaling
        // with 1/length left short folds displacing too little to self-start
        self.m1 = M1 * l * l * qm;
        self.m2 = M2 * l * l * qm;
        self.k1 = K1 * qk;
        self.k2 = K2 * qk;
        self.kc = KC * self.cfg.fold.coupling * qk;
        self.r1 = 2.0 * ZETA1 * self.cfg.fold.damping * sqrt(self.m1 * self.k1);
        self.r2 = 2.0 * ZETA2 * self.cfg.fold.damping * sqrt(self.m2 * self.k2);
        self.r1c = self.r1 + 2.0 * ZETA_CONTACT * sqrt(self.m1 * self.k1);
        self.r2c = self.r2 + 2.0 * ZETA_CONTACT * sqrt(self.m2 * self.k2);
        let hard = 1.0 + 2.0 * d.brightness;
        self.c1 = 3.0 * self.k1 * hard;
        self.c2 = 3.0 * self.k2 * hard;
        self.d1 = D1;
        self.d2 = D2;
        if self.cfg.register.enabled {
            let bd = clamp(self.cfg.register.break_depth, 0.0, 1.0) * self.register;
            self.m1 *= 1.0 - 0.4 * bd;
            self.m2 *= 1.0 - 0.25 * bd;
            self.d1 *= 1.0 - 0.3 * bd;
            self.kc *= 1.0 + 0.4 * bd;
            self.c1 *= 1.0 - 0.2 * bd;
            self.c2 *= 1.0 - 0.2 * bd;
        }
        let rest = (self.cfg.fold.rest_area * (1.5 - 1.6 * d.tension) + 0.008 * clamp(self.cfg.register.break_depth, 0.0, 1.0) * self.register) * self.fold_len / 1.4;
        self.a0 = (1.0 - g.closure) * (rest + g.abduction) - g.closure * 0.15;
        self.a01 = self.a0 + self.cfg.fold.convergence_area * self.fold_len / 1.4;
    }

    /// One sample of the two-mass fold; returns the glottal area.
    #[inline]
    pub fn fold_step(&mut self, ps_in: f64, pe_in: f64, g: &mut ParametricGlottis) -> f64 {
        self.ps_sm += self.p_coef * (ps_in - self.ps_sm);
        self.pe_sm += self.p_coef * (pe_in - self.pe_sm);
        let ps = self.ps_sm + self.fb * (ps_in - self.ps_sm);
        let pe = self.pe_sm + self.fb * (pe_in - self.pe_sm);
        let l2 = 2.0 * self.fold_len;
        let a1 = self.a01 + l2 * self.x1;
        let a2 = self.a0 + l2 * self.x2;
        let amin = js_min(a1, a2);
        let p1 = if a1 > 0.0 {
            if amin > 0.0 {
                let ratio = amin / a1;
                ps - (ps - pe) * ratio * ratio
            } else {
                ps
            }
        } else {
            0.0
        };
        let p2 = if a2 > 0.0 && amin > 0.0 { pe } else { 0.0 };
        let dt = 1.0 / self.fs;
        let f1 = self.fold_len * self.d1 * p1;
        let f2 = self.fold_len * self.d2 * p2;
        let coupling = self.kc * (self.x1 - self.x2);
        let (coll1, r1) = if a1 < 0.0 { (self.c1 * (self.x1 + self.a01 / l2), self.r1c) } else { (0.0, self.r1) };
        let (coll2, r2) = if a2 < 0.0 { (self.c2 * (self.x2 + self.a0 / l2), self.r2c) } else { (0.0, self.r2) };
        self.v1 += dt * (f1 - r1 * self.v1 - self.k1 * self.x1 - coupling - coll1) / self.m1;
        self.v2 += dt * (f2 - r2 * self.v2 - self.k2 * self.x2 + coupling - coll2) / self.m2;
        self.x1 += dt * self.v1;
        self.x2 += dt * self.v2;
        let vib = js_max(0.0, js_min(self.a01 + l2 * self.x1, self.a0 + l2 * self.x2));
        let chink = g.params.chink * (1.0 - 0.92 * g.params.closure);
        let area = vib + chink;
        self.track_cycle(vib, g);
        g.area = area;
        area
    }

    /// Period from rising midpoint crossings of the vibratory area, and the pitch loop on it.
    #[inline]
    fn track_cycle(&mut self, x: f64, g: &mut ParametricGlottis) {
        self.since += 1.0;
        if x > self.env_hi {
            self.env_hi = x;
        } else {
            self.env_hi -= (self.env_hi - x) * 0.0006;
        }
        if x < self.env_lo {
            self.env_lo = x;
        } else {
            self.env_lo += (x - self.env_lo) * 0.0006;
        }
        let mid = 0.5 * (self.env_hi + self.env_lo);
        let refractory = 0.4 * self.fs / js_max(40.0, self.drive.f0_target);
        if self.prev < mid && x >= mid && self.since >= refractory && self.env_hi - self.env_lo > 1e-3 {
            let frac = (mid - self.prev) / js_max(1e-12, x - self.prev);
            let exact = self.since - 1.0 + frac;
            if self.last_cross >= 0.0 {
                let period = exact + (1.0 - self.last_cross);
                self.jit = 1.0 + g.params.jitter * (1.0 + 3.0 * self.fatigue) * self.rng.gauss();
                let f = self.fs / js_max(1.0, period);
                self.f0_meas = f;
                self.voiced_count = js_min(self.voiced_count + 1.0, 20.0);
                if self.cfg.fold.pitch_loop && self.voiced_count >= 3.0 {
                    let tau = js_max(1.0, self.cfg.fold.pitch_loop_tau_ms) * 1e-3;
                    let alpha = 1.0 - exp(-(period / self.fs) / tau);
                    // octave-sized errors are detector glitches at gesture boundaries, not pitch
                    let err = ln(self.drive.f0_target / f);
                    if err.abs() < 0.4 {
                        self.trim += alpha * err;
                    }
                    self.trim = clamp(self.trim, -0.9, 0.9);
                }
                g.f0_now = f;
            }
            self.last_cross = 1.0 - frac;
            self.since = 0.0;
        }
        if self.since > 0.03 * self.fs {
            self.voiced_count = 0.0;
            self.last_cross = -1.0;
            self.f0_meas = 0.0;
            g.f0_now = 0.0;
        }
        g.voicing = js_min(1.0, self.voiced_count / 5.0);
        self.prev = x;
    }

    /// Control-rate register state: pitch against a hysteretic passaggio, first-order transition.
    pub fn register_step(&mut self, dt: f64, p_cmh2o: f64) {
        self.p_cmh2o = p_cmh2o;
        let c = &self.cfg.register;
        if !c.enabled {
            return;
        }
        let midi = hz_to_midi(js_max(20.0, self.drive.f0_target));
        let target = match c.mode.as_str() {
            "chest" => 0.0,
            "head" => 1.0,
            "mix" => clamp(c.mix, 0.0, 1.0),
            _ => {
                let up = if self.register > 0.5 { -0.5 } else { 0.5 };
                let thr = c.passaggio_midi + c.hysteresis_semi * up + c.pressure_slope * (p_cmh2o - 9.0);
                smoothstep(thr - 0.5 * c.width_semi, thr + 0.5 * c.width_semi, midi)
            }
        };
        let a = 1.0 - exp(-dt / js_max(1e-3, c.tau_ms * 1e-3));
        self.register += a * (target - self.register);
    }

    /// Source settings from absolute pitch: replaces the song-relative plan.
    /// Returns (tension, brightness, breathiness).
    pub fn map_source(&self, f0: f64, p_cmh2o: f64) -> (f64, f64, f64) {
        let c = &self.cfg.source_map;
        let midi = hz_to_midi(js_max(20.0, f0));
        let t = interp(&c.midi, &c.tension, midi) + c.loudness_tension * (p_cmh2o - 9.0);
        (clamp(t, 0.0, 1.0), interp(&c.midi, &c.brightness, midi), interp(&c.midi, &c.breathiness, midi))
    }

    /// Tract adjustment for the pitch: F1 is computed from the live area function; the jaw and lips
    /// open when F1 would fall under f0, and the larynx rises with pitch. Adds to the gesture blend.
    pub fn tune_tract(&mut self, blend: &mut [Blended; N_CONTROL], airway: &HumanAirway, dt: f64) {
        let c = self.cfg.tract.clone();
        if !c.enabled {
            return;
        }
        self.f1_counter += 1;
        if self.f1_counter >= 8 {
            self.f1_counter = 0;
            self.f1_est = estimate_f1(airway).unwrap_or(0.0);
        }
        let f0 = self.drive.f0_target;
        let need = if self.f1_est > 0.0 { js_max(0.0, c.margin * f0 / self.f1_est - 1.0) } else { 0.0 };
        let a = 1.0 - exp(-dt / js_max(1e-3, c.tau_ms * 1e-3));
        self.jaw_delta += a * (js_min(c.jaw_max, c.jaw_gain * need) - self.jaw_delta);
        self.lip_delta += a * (c.lip_gain * need - self.lip_delta);
        let lar = c.larynx_per_semi * (hz_to_midi(js_max(20.0, f0)) - c.ref_midi);
        add_to_blend(blend, ArticKey::Jaw, self.jaw_delta);
        add_to_blend(blend, ArticKey::LipAp, self.lip_delta);
        add_to_blend(blend, ArticKey::TbY, -c.tongue_gain * js_min(0.75, need));
        add_to_blend(blend, ArticKey::Larynx, clamp(lar, -1.2, 1.2));
    }

    /// Accumulate the glottal volume flow (cm³/s, positive out of the lungs).
    #[inline]
    pub fn add_flow(&mut self, u: f64) {
        self.flow_acc += u;
        self.flow_n += 1.0;
    }

    /// Control-rate lung state: integrates flow, returns the pressure the lungs can actually supply.
    pub fn breath_step(&mut self, dt: f64, p_target: f64) -> f64 {
        let c = &self.cfg.breath;
        if !c.enabled {
            return p_target;
        }
        let u = if self.flow_n > 0.0 { self.flow_acc / self.flow_n } else { 0.0 };
        self.flow_acc = 0.0;
        self.flow_n = 0.0;
        let inward = if u < 0.0 { c.inhale_gain } else { 1.0 };
        self.volume = clamp(self.volume - inward * u * dt, 0.0, self.vital);
        let frac = self.volume / js_max(1.0, self.vital);
        let rate = dt / js_max(0.1, c.fatigue_s);
        self.fatigue = clamp(self.fatigue + if frac < c.fatigue_below { rate } else { -rate }, 0.0, 1.0);
        if p_target <= 0.0 {
            return p_target;
        }
        let limit = c.max_pressure * CM_H2O * smoothstep(0.0, js_max(1e-3, c.reserve_fraction), frac) * (1.0 - 0.25 * self.fatigue);
        js_min(p_target, limit)
    }

    /// Habitual articulatory posture, added to every gesture target.
    pub fn apply_setting(&self, blend: &mut [Blended; N_CONTROL]) {
        let a = &self.cfg.anatomy;
        if !a.enabled {
            return;
        }
        add_to_blend(blend, ArticKey::Jaw, a.setting_jaw);
        add_to_blend(blend, ArticKey::TbX, a.setting_tongue_x);
        add_to_blend(blend, ArticKey::TbY, a.setting_tongue_y);
        add_to_blend(blend, ArticKey::Larynx, a.setting_larynx);
        add_to_blend(blend, ArticKey::LipProt, a.setting_lip_prot);
    }

    /// Records one row every `TRACE_DT` of voice clock when tracing.
    pub fn record_trace(&mut self, t: f64, dt: f64, p_lung: f64) {
        let Some(tr) = self.trace.as_mut() else { return };
        self.trace_counter -= dt;
        if self.trace_counter > 0.0 {
            return;
        }
        self.trace_counter += TRACE_DT;
        let voicing = js_min(1.0, self.voiced_count / 5.0);
        tr.push([t, self.drive.f0_target, self.f0_meas, voicing, self.q, self.a0, p_lung / CM_H2O, self.drive.tension, self.register, self.f1_est, self.jaw_delta, self.drive.brightness, self.volume / js_max(1.0, self.vital), self.fatigue]);
    }
}

#[inline]
fn add_to_blend(blend: &mut [Blended; N_CONTROL], key: ArticKey, delta: f64) {
    let b = &mut blend[ControlKey::Artic(key).index()];
    if b.weight > 0.0 {
        b.value += delta;
    }
}

/// Piecewise-linear lookup (flat outside the knots).
pub fn interp(xs: &[f64], ys: &[f64], x: f64) -> f64 {
    if xs.is_empty() {
        return 0.0;
    }
    if x <= xs[0] {
        return ys[0];
    }
    for i in 1..xs.len() {
        if x <= xs[i] {
            return lerp(ys[i - 1], ys[i], (x - xs[i - 1]) / js_max(1e-9, xs[i] - xs[i - 1]));
        }
    }
    ys[ys.len() - 1]
}

/// First resonance of the lossless plane-wave chain from a closed glottis to open lips, by a chain
/// matrix over the live areas. `None` while the tract is occluded (consonants).
pub fn estimate_f1(a: &HumanAirway) -> Option<f64> {
    let k2 = a.body.scale * a.body.scale;
    if a.or_areas.iter().chain(a.ph_areas.iter()).any(|x| *x < 0.04 * k2) {
        return None;
    }
    let dph = a.ph_len / a.n_ph as f64;
    let dor = a.or_len / a.n_or as f64;
    let sum_d = |f: f64| -> f64 {
        let wc = core::f64::consts::TAU * f / C_SOUND;
        let (mut aa, mut bb, mut cc, mut dd) = (1.0, 0.0, 0.0, 1.0);
        let mut section = |area: f64, len: f64| {
            let k = wc * len;
            let (c1, s1) = (cos(k), sin(k));
            let z = 1.0 / js_max(1e-3, area); // characteristic impedance up to a constant
            let (a2, b2, c2, d2) = (c1, z * s1, s1 / z, c1);
            let (a0, b0, c0, d0) = (aa, bb, cc, dd);
            aa = a0 * a2 - b0 * c2;
            bb = a0 * b2 + b0 * d2;
            cc = c0 * a2 + d0 * c2;
            dd = d0 * d2 - c0 * b2;
        };
        for x in a.ph_areas.iter() {
            section(*x, dph);
        }
        for x in a.or_areas.iter() {
            section(*x, dor);
        }
        dd
    };
    let mut f = 120.0;
    let mut prev = sum_d(f);
    while f < 1500.0 {
        let next = f + 10.0;
        let d = sum_d(next);
        if prev * d <= 0.0 {
            return Some(f + 10.0 * prev / js_max(1e-30, prev - d));
        }
        prev = d;
        f = next;
    }
    None
}

/// Seeded smooth multiplicative irregularity for `n` tract sections (mean 1).
pub fn area_perturbation(n: usize, depth: f64, seed: u32) -> Vec<f64> {
    let mut rng = Rng::new(seed);
    let phases = [rng.next() * core::f64::consts::TAU, rng.next() * core::f64::consts::TAU, rng.next() * core::f64::consts::TAU];
    (0..n)
        .map(|i| {
            let u = i as f64 / js_max(1.0, n as f64 - 1.0) * core::f64::consts::TAU;
            1.0 + depth * (0.5 * sin(1.5 * u + phases[0]) + 0.3 * sin(3.0 * u + phases[1]) + 0.2 * sin(5.0 * u + phases[2]))
        })
        .collect()
}
