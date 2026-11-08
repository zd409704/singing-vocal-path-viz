// VOCAL PATH dashboard. One canvas renderer shared by the video exporter and the local page.
// Every frame is a pure function of (data, t), so video and page show the same thing.
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.VocalPath = factory();
})(typeof self !== "undefined" ? self : this, function () {
  const W = 1920, H = 1080;
  const C = {
    bg: "#0a0d12", panel: "#0d1117", line: "#20262f", dim: "#6e7681", text: "#a8acb3",
    cream: "#e9e3d3", gold: "#f0b04a", red: "#e8553f", teal: "#57c9a6", blue: "#4f94b8",
    note: "#2f6b5e", wire: "#2b4a5e",
  };
  const MONO = '"IBM Plex Mono", ui-monospace, Menlo, monospace';
  const SANS = '"IBM Plex Sans", system-ui, sans-serif';
  const NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
  const ROLL = { x0: 1154, x1: 1888, playX: 1418, top: 108, bottom: 796, pxPerSec: 82, hiMidi: 74, loMidi: 55, hiY: 156, loY: 778 };
  const ROWS = ["tongue_height", "tongue_back", "tongue_tip", "jaw", "lips", "velum", "airflow"];

  const lerp = (a, b, k) => a + (b - a) * k;
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const frac = (x) => x - Math.floor(x);
  const rand = (i, s) => frac(Math.sin(i * 127.1 + s * 311.7) * 43758.5453);
  const noteY = (m) => lerp(ROLL.loY, ROLL.hiY, (m - ROLL.loMidi) / (ROLL.hiMidi - ROLL.loMidi));
  const noteName = (m) => NAMES[((m % 12) + 12) % 12] + (Math.floor(m / 12) - 1);
  const fmtTime = (t) => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, "0")}`;

  function spline(points, closed, steps = 12) {
    const out = [], n = points.length;
    const P = (i) => (closed ? points[(i + n) % n] : points[clamp(i, 0, n - 1)]);
    for (let i = 0; i < (closed ? n : n - 1); i++) {
      const [p0, p1, p2, p3] = [P(i - 1), P(i), P(i + 1), P(i + 2)];
      for (let j = 0; j < steps; j++) {
        const t = j / steps, t2 = t * t, t3 = t2 * t;
        out.push([
          0.5 * (2 * p1[0] + (p2[0] - p0[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (3 * p1[0] - p0[0] - 3 * p2[0] + p3[0]) * t3),
          0.5 * (2 * p1[1] + (p2[1] - p0[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (3 * p1[1] - p0[1] - 3 * p2[1] + p3[1]) * t3),
        ]);
      }
    }
    if (!closed) out.push(points[n - 1]);
    return out;
  }
  function trace(ctx, pts, closed) {
    ctx.beginPath();
    pts.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])));
    if (closed) ctx.closePath();
  }
  function stroke(ctx, pts, color, width = 1, alpha = 1, closed = false) {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.lineJoin = "round";
    ctx.lineCap = "round";
    trace(ctx, pts, closed);
    ctx.stroke();
    ctx.restore();
  }
  function text(ctx, s, x, y, font, color, align = "left") {
    ctx.font = font;
    ctx.fillStyle = color;
    ctx.textAlign = align;
    ctx.textBaseline = "alphabetic";
    ctx.fillText(s, x, y);
  }
  function resample(pts, count) {
    const dist = [0];
    for (let i = 1; i < pts.length; i++) dist[i] = dist[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    const out = [];
    let j = 0;
    for (let k = 0; k < count; k++) {
      const d = (k / (count - 1)) * dist[dist.length - 1];
      while (j < dist.length - 2 && dist[j + 1] < d) j++;
      const f = (d - dist[j]) / Math.max(1e-6, dist[j + 1] - dist[j]);
      out.push([lerp(pts[j][0], pts[j + 1][0], f), lerp(pts[j][1], pts[j + 1][1], f)]);
    }
    return out;
  }
  // Dashes travelling along a path; `phase` is integrated airflow, so they reverse on inhale.
  function drawFlow(ctx, path, phase, flow, opts) {
    const { count, seed, width = 2, spread = 3, rate = 0.5, color } = opts;
    const n = path.length;
    for (let i = 0; i < count; i++) {
      const s = frac(rand(i, seed) + phase * rate);
      const idx = Math.floor(s * (n - 2));
      const [a, b] = [path[idx], path[idx + 1]];
      const dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy) || 1;
      const nx = -dy / len, ny = dx / len;
      const off = (rand(i, seed + 2) - 0.5) * spread * 2;
      const l = 4 + 5 * rand(i, seed + 4);
      const x = a[0] + nx * off, y = a[1] + ny * off;
      ctx.globalAlpha = clamp(flow * 1.5, 0, 1) * (0.35 + 0.65 * rand(i, seed + 6));
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.beginPath();
      ctx.moveTo(x - (dx / len) * l, y - (dy / len) * l);
      ctx.lineTo(x + (dx / len) * l, y + (dy / len) * l);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }

  // ---- Static geometry ----
  const HEAD = [[256, 117], [320, 124], [362, 168], [372, 226], [369, 258], [402, 292], [375, 306], [380, 344], [362, 396], [326, 432], [296, 436], [290, 512], [352, 562], [428, 598], [442, 980]];
  const BACK = [[70, 980], [76, 600], [146, 562], [186, 530], [198, 450], [168, 372], [132, 318], [124, 240], [140, 172], [188, 130]];
  const BODY = spline([...HEAD, ...BACK], true, 10);
  const BODY_TOP = spline(HEAD.slice(0, 12).concat(), false, 10);
  const BODY_BACK = spline(BACK.slice(2).concat([HEAD[0]]), false, 10);
  const LOBE_L = [[188, 612], [120, 700], [88, 790], [108, 880], [176, 944], [226, 880], [244, 760], [226, 660]];
  const LOBE_R = [[316, 612], [384, 700], [420, 790], [398, 880], [322, 944], [278, 880], [262, 760], [282, 660]];
  const AIR_L = spline([[150, 880], [200, 800], [232, 745], [256, 690], [256, 600], [260, 480], [260, 430], [252, 372], [272, 332], [340, 326], [400, 324], [425, 330]], false, 16);
  const AIR_R = spline([[345, 880], [312, 800], [280, 745], [256, 690], [256, 600], [260, 480], [260, 430], [252, 372], [272, 332], [340, 326], [400, 324], [425, 330]], false, 16);

  function drawStatic(ctx) {
    ctx.fillStyle = C.bg;
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = C.line;
    ctx.lineWidth = 1;
    for (const [x, y, w, h] of [[20, 65, 520, 945], [552, 65, 540, 539], [552, 616, 540, 394], [1104, 65, 796, 945]]) {
      ctx.fillStyle = C.panel;
      ctx.fillRect(x, y, w, h);
      ctx.strokeRect(x + 0.5, y + 0.5, w, h);
    }
    const title = `600 14px ${SANS}`;
    text(ctx, "Full-body airway", 36, 92, title, C.text);
    text(ctx, "Oral cavity & vocal tract · Midsagittal", 568, 92, title, C.text);
    text(ctx, "Current phonation", 568, 644, title, C.text);
    text(ctx, "Pitch", 1120, 92, title, C.text);

    // Body wireframe, clipped to the silhouette.
    ctx.save();
    trace(ctx, BODY, true);
    ctx.clip();
    ctx.strokeStyle = C.wire;
    ctx.globalAlpha = 0.28;
    ctx.lineWidth = 1;
    for (let y = 110; y < 990; y += 18) {
      ctx.beginPath();
      for (let x = 60; x <= 450; x += 8) {
        const yy = y + Math.sin((x - 256) / 95) * (y > 560 ? 18 : 7);
        x === 60 ? ctx.moveTo(x, yy) : ctx.lineTo(x, yy);
      }
      ctx.stroke();
    }
    for (let k = -8; k <= 8; k++) {
      ctx.beginPath();
      for (let y = 110; y <= 990; y += 10) {
        const half = y < 440 ? 130 : y < 560 ? 62 : 190;
        const x = 256 + (k / 8) * half * Math.cos(((y - 560) / 900) * 1.2);
        y === 110 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.stroke();
    }
    ctx.restore();
    stroke(ctx, BODY_TOP, "#f0ece0", 2, 0.9);
    stroke(ctx, BODY_BACK, "#f0ece0", 2, 0.75);
    stroke(ctx, spline([[70, 980], [76, 600], [146, 562]], false, 8), C.dim, 1, 0.55);
    stroke(ctx, spline([[428, 598], [442, 980]], false, 8), C.dim, 1, 0.55);
    stroke(ctx, spline([[244, 410], [234, 340], [250, 282], [318, 256], [350, 296], [362, 340]], false, 8), C.cream, 1.2, 0.5);
    stroke(ctx, spline([[300, 372], [340, 380], [358, 348]], false, 8), C.cream, 1.2, 0.5);

    // Pitch rows and labels.
    const R = ROLL;
    for (let m = R.loMidi; m <= R.hiMidi; m++) {
      const y = noteY(m);
      const black = [1, 3, 6, 8, 10].includes(((m % 12) + 12) % 12);
      if (!black) {
        ctx.fillStyle = "#121820";
        ctx.fillRect(R.x0, y - 16, R.x1 - R.x0, 32);
        text(ctx, noteName(m), 1145, y + 4, `12px ${MONO}`, C.dim, "right");
      }
      ctx.fillStyle = "#171d25";
      ctx.fillRect(R.x0, y + 16, R.x1 - R.x0, 1);
    }
    text(ctx, "Breath", 1113, 880, `600 12px ${SANS}`, C.dim);
    text(ctx, "Phones", 1113, 950, `600 12px ${SANS}`, C.dim);

    // Pitch chart legend.
    const legend = `12px ${SANS}`;
    const items = [["Recorded notes", C.note, 1540], ["Stable", C.teal, 1668], ["Deviation", C.red, 1740]];
    for (const [label, color, x] of items) {
      ctx.fillStyle = color;
      ctx.fillRect(x, 82, 18, 10);
      text(ctx, label, x + 24, 92, legend, C.text);
    }
  }

  // ---- Midsagittal tract ----
  function tractGeometry(a) {
    const jawAng = (a.jaw * 15 * Math.PI) / 180;
    const pivot = [752, 250];
    const rot = ([x, y]) => {
      const dx = x - pivot[0], dy = y - pivot[1];
      return [pivot[0] + dx * Math.cos(jawAng) - dy * Math.sin(jawAng), pivot[1] + dx * Math.sin(jawAng) + dy * Math.cos(jawAng)];
    };
    const peakX = lerp(838, 700, a.tongue_back);
    const peakY = lerp(362, 238, a.tongue_height) + a.jaw * 26;
    const tip = [lerp(868, 900, a.tongue_tip), lerp(352 + a.jaw * 28, 256, a.tongue_tip)];
    const blade = [lerp(peakX, tip[0], 0.55), lerp(peakY, tip[1], 0.5) - 6 + a.tongue_tip * 8];
    const top = spline([[668, 395], [668, 352], [lerp(668, peakX, 0.45), lerp(352, peakY, 0.8)], [peakX, peakY], blade, tip], false, 14);
    const under = spline([tip, [lerp(tip[0], 830, 0.5), lerp(tip[1], 392 + a.jaw * 34, 0.75)], [790, 400 + a.jaw * 32], [720, 408 + a.jaw * 20], [672, 396]], false, 10);
    return { rot, top, under, tongue: [...top, ...under], tip };
  }

  function palateY(x) {
    // Roof of the mouth, front (x=905) to the velum join (x=738).
    if (x < 738) return 208;
    if (x > 905) return 240;
    return lerp(208, 238, (x - 738) / 167) + Math.sin(((x - 738) / 167) * Math.PI) * 4;
  }

  function drawTongueShape(ctx, geo, alpha = 1) {
    ctx.save();
    ctx.globalAlpha = alpha;
    trace(ctx, geo.tongue, true);
    ctx.fillStyle = "rgba(232,85,63,0.52)";
    ctx.fill();
    ctx.strokeStyle = C.red;
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.restore();
  }

  function drawTract(ctx, a, phase, flow, inhale, airflow, pitchPhase) {
    const geo = tractGeometry(a);
    const { rot } = geo;
    // Nasal cavity.
    stroke(ctx, [[668, 152], [708, 124], [812, 112], [918, 135], [996, 205]], C.blue, 1.4, 0.9);
    stroke(ctx, [[735, 192], [828, 187], [905, 215]], C.blue, 1.2, 0.8);
    // Head profile.
    stroke(ctx, spline([[938, 65], [928, 100], [968, 150], [1008, 206], [964, 228], [948, 226]], false, 10), C.cream, 1.2, 0.6);
    stroke(ctx, spline([[648, 172], [706, 124]], false, 4), C.cream, 1.2, 0.5);
    // Dashed skull and neck references.
    ctx.save();
    ctx.setLineDash([4, 5]);
    stroke(ctx, spline([[584, 205], [565, 280], [556, 355], [600, 400], [700, 442], [790, 470], [860, 482]], false, 8), C.dim, 1, 0.55);
    ctx.restore();
    // Back wall of the pharynx, down to the trachea.
    stroke(ctx, spline([[648, 172], [644, 250], [644, 340], [650, 460], [660, 560]], false, 10), C.cream, 2, 0.85);
    // Hard palate, velum, upper teeth and upper lip.
    const palate = spline([[738, 208], [800, 208], [860, 218], [905, 235], [918, 250]], false, 10);
    stroke(ctx, palate, C.cream, 2, 0.9);
    const uvula = [lerp(660, 668, a.velum), lerp(208, 268, a.velum)];
    stroke(ctx, spline([[738, 208], [705, lerp(208, 216, a.velum)], [680, lerp(208, 240, a.velum)], uvula], false, 10), C.teal, 3, 0.95);
    ctx.fillStyle = "#d9d3c4";
    ctx.fillRect(917, 240, 13, 24);
    const lipPush = a.lips * 20;
    const lipGap = 62 + a.jaw * 58 - a.lips * 34;
    const upLip = spline([[918, 234 - a.lips * 3], [946 + lipPush, 231], [966 + lipPush, 240], [944 + lipPush, 249], [921, 248]], true, 8);
    trace(ctx, upLip, true);
    ctx.fillStyle = "rgba(232,85,63,0.6)";
    ctx.fill();
    ctx.strokeStyle = C.red;
    ctx.lineWidth = 1.3;
    ctx.stroke();

    // Jaw: lower teeth, lower lip, chin and floor of the mouth rotate together.
    const lowY = 249 + clamp(lipGap, 0, 200);
    const lowLip = spline([[920, lowY + 4], [946 + lipPush, lowY], [962 + lipPush, lowY + 12], [944 + lipPush, lowY + 30], [921, lowY + 22]], true, 8);
    trace(ctx, lowLip, true);
    ctx.fillStyle = "rgba(232,85,63,0.6)";
    ctx.fill();
    ctx.strokeStyle = C.red;
    ctx.stroke();
    ctx.fillStyle = "#d9d3c4";
    ctx.fillRect(884, lowY - 4, 12, 24);
    const chin = spline([rot([920, 300]), rot([906, 380]), rot([900, 408]), rot([862, 452]), rot([806, 472]), rot([756, 462])], false, 10);
    stroke(ctx, chin, C.cream, 1.2, 0.6);
    // Larynx front wall.
    stroke(ctx, spline([[672, 400], [700, 430], [716, 500], [736, 560], [750, 603]], false, 10), C.cream, 2, 0.85);
    stroke(ctx, spline([[756, 462], [738, 500], [745, 603]], false, 8), C.dim, 1, 0.7);

    drawTongueShape(ctx, geo);

    // Glottis markers.
    const open = 6 + 6 * Math.sin(pitchPhase) * flow;
    ctx.fillStyle = C.gold;
    for (const sign of [-1, 1]) {
      ctx.beginPath();
      ctx.moveTo(sign < 0 ? 660 : 722, 498);
      ctx.lineTo(sign < 0 ? 660 : 722, 522);
      ctx.lineTo(691 + sign * open, 510);
      ctx.closePath();
      ctx.fill();
    }

    // Air path follows the current gap between palate and tongue, then leaves between the lips.
    const oral = [];
    for (let x = 700; x <= 1000; x += 20) {
      const tongueTop = geo.top.reduce((best, p) => (Math.abs(p[0] - x) < Math.abs(best[0] - x) ? p : best), geo.top[0])[1];
      const floor = x > 900 ? lowY + 6 : tongueTop;
      oral.push([x, (palateY(x) + Math.min(floor, 400)) / 2 + 2]);
    }
    const mouth = resample(spline([[688, 590], [688, 510], [668, 420], [662, 330], [678, oral[0][1]], ...oral, [1060, oral[oral.length - 1][1]]], false, 8), 130);
    const nasal = resample(spline([[688, 590], [688, 510], [668, 420], [662, 330], [668, 230], [720, 160], [812, 148], [918, 172], [1010, 230], [1060, 248]], false, 8), 130);
    const airColor = inhale > 0.05 ? C.blue : C.gold;
    const oralFlow = Math.max(airflow, inhale * 0.5) * (1 - a.velum * 0.7);
    ctx.lineCap = "round";
    drawFlow(ctx, mouth, phase, oralFlow, { count: 52, seed: 3, spread: 6, rate: 0.55, color: airColor });
    drawFlow(ctx, nasal, phase, Math.max(airflow, inhale * 0.5) * a.velum, { count: 36, seed: 7, spread: 6, rate: 0.55, color: airColor });

    const lf = `12px ${SANS}`;
    text(ctx, "Nasal cavity", 790, 134, lf, C.dim);
    text(ctx, "Hard palate", 770, 228, lf, C.dim);
    text(ctx, "Soft palate", 562, 196, lf, C.teal);
    text(ctx, "Pharynx", 584, 312, lf, C.dim);
    text(ctx, "Tongue", 755, 342, lf, C.cream);
    text(ctx, "Jaw", rot([800, 440])[0] - 10, rot([800, 440])[1], lf, C.dim);
    text(ctx, "Lips", 1000, 300, lf, C.dim);
    text(ctx, "Glottis", 744, 515, lf, C.dim);
    return geo;
  }

  // ---- Whole body ----
  function drawBody(ctx, data, s, phase) {
    const v = s.lung;
    const sx = 0.82 + 0.26 * v, sy = 0.86 + 0.18 * v;
    const scaled = (pts) => pts.map(([x, y]) => [256 + (x - 256) * sx, 640 + (y - 640) * sy]);
    for (const lobe of [LOBE_L, LOBE_R]) {
      const pts = spline(scaled(lobe), true, 12);
      stroke(ctx, pts, C.blue, 1.4, 0.65, true);
      ctx.save();
      trace(ctx, pts, true);
      ctx.clip();
      ctx.globalAlpha = 0.28;
      ctx.strokeStyle = C.blue;
      ctx.lineWidth = 1;
      for (let y = 590; y < 980; y += 22) {
        ctx.beginPath();
        ctx.moveTo(60, y);
        ctx.quadraticCurveTo(256, y + 20, 450, y);
        ctx.stroke();
      }
      for (let x = 70; x < 450; x += 28) {
        ctx.beginPath();
        ctx.moveTo(x, 590);
        ctx.quadraticCurveTo(256 + (x - 256) * 0.5, 800, x, 985);
        ctx.stroke();
      }
      ctx.restore();
    }
    // Ribs and diaphragm; the diaphragm drops as the lungs fill.
    for (let k = 0; k < 8; k++) {
      const y = 590 + k * 48 + v * 6;
      stroke(ctx, spline([[78, y + 6], [256, y - 10 - v * 4], [434, y + 6]], false, 6), C.dim, 1, 0.45);
      stroke(ctx, spline([[78, y + 6], [256, y + 22 + v * 4], [434, y + 6]], false, 6), C.dim, 1, 0.3);
    }
    const dy = 920 + v * 38;
    for (let k = 0; k < 4; k++) {
      stroke(ctx, spline([[74 + k * 18, 970], [190, dy - 45 + k * 12], [256, dy - 60 + k * 16], [320, dy - 45 + k * 12], [436 - k * 18, 970]], false, 8), C.red, 1.1, 0.55);
    }
    // Trachea rings.
    for (let y = 470; y < 620; y += 14) stroke(ctx, [[245, y], [272, y + 2]], C.dim, 1, 0.5);

    // Mini tongue, reusing the tract geometry at a smaller scale.
    ctx.save();
    ctx.translate(228, 202);
    ctx.scale(0.32, 0.32);
    ctx.translate(-560, 60);
    drawTongueShape(ctx, tractGeometry(s), 0.95);
    ctx.restore();

    const color = s.inhale > 0.05 ? C.blue : C.gold;
    ctx.lineCap = "round";
    const f = Math.max(s.airflow, s.inhale * 0.55);
    drawFlow(ctx, resample(AIR_L, 140), phase, f, { count: 34, seed: 11, spread: 3.5, rate: 0.5, color, width: 1.6 });
    drawFlow(ctx, resample(AIR_R, 140), phase, f, { count: 34, seed: 13, spread: 3.5, rate: 0.5, color, width: 1.6 });
    text(ctx, `Lung volume (illustrative)  ${Math.round(s.lung * 100)}%`, 36, 994, `13px ${MONO}`, C.text);
  }

  // ---- Current phonation ----
  function drawPhonation(ctx, data, s, t) {
    const syl = currentSyllable(data, t);
    if (syl) {
      const size = syl.grapheme.length > 3 ? 92 : 124;
      text(ctx, syl.grapheme, 578, 800, `700 ${size}px ${SANS}`, C.cream);
      text(ctx, syl.pron, 578, 845, `600 30px ${MONO}`, C.gold);
    } else {
      text(ctx, "breath", 578, 845, `600 30px ${MONO}`, C.blue);
    }
    if (s.midi != null) {
      const nearest = Math.round(s.midi);
      const cents = Math.round((s.midi - nearest) * 100);
      text(ctx, noteName(nearest), 578, 890, `600 26px ${MONO}`, C.cream);
      text(ctx, `${cents >= 0 ? "+" : "−"}${Math.abs(cents)}¢`, 662, 890, `600 26px ${MONO}`, C.cream);
    } else {
      text(ctx, "—", 578, 890, `600 26px ${MONO}`, C.dim);
    }
    // Phone chips for the current syllable.
    if (syl) {
      let x = 578;
      const spans = data.phones.filter((p) => p.start < syl.end + 0.3 && p.start >= syl.start - 0.5 && p.syllable === syl.index);
      for (const p of spans) {
        const active = t >= p.start && t < p.end;
        const w = Math.max(28, 14 + p.ipa.length * 14);
        ctx.fillStyle = active ? "#7a5a26" : "#1a2029";
        ctx.fillRect(x, 916, w, 30);
        text(ctx, p.ipa, x + w / 2, 937, `15px ${MONO}`, active ? "#fff" : C.text, "center");
        x += w + 6;
      }
    }
    const rows = [["Tongue height", s.tongue_height, C.red], ["Tongue backness", s.tongue_back, C.red],
      ["Tongue tip", s.tongue_tip, C.red], ["Jaw opening", s.jaw, C.cream], ["Lip rounding", s.lips, C.cream],
      ["Velum opening", s.velum, C.cream], ["Airflow", s.airflow, C.gold]];
    rows.forEach(([label, value, color], i) => {
      const y = 677 + i * 31;
      text(ctx, label, 900, y + 9, `12px ${SANS}`, C.text, "right");
      ctx.fillStyle = "#1a2029";
      ctx.fillRect(910, y, 160, 9);
      ctx.fillStyle = color;
      ctx.fillRect(910, y, 160 * clamp(value, 0, 1), 9);
    });
    text(ctx, "Vocal folds, top view (slowed)", 934, 950, `12px ${SANS}`, C.text, "right");
    ctx.strokeStyle = C.dim;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.ellipse(1000, 946, 54, 40, 0, 0, Math.PI * 2);
    ctx.stroke();
    // Abducted while breathing, nearly closed and vibrating while voiced. Slowed for viewing.
    const breathing = s.voiced ? 0 : 1;
    const vibrate = s.voiced ? (Math.sin(t * 2 * Math.PI * 7) + 1) / 2 : 0;
    const gap = lerp(1.5 + vibrate * 6, 14, breathing);
    ctx.strokeStyle = C.gold;
    ctx.lineWidth = 3;
    ctx.lineCap = "round";
    for (const sign of [-1, 1]) {
      ctx.beginPath();
      ctx.moveTo(1000, 918);
      ctx.quadraticCurveTo(1000 + sign * (gap + 2), 945, 1000 + sign * gap, 974);
      ctx.stroke();
    }
  }

  function currentSyllable(data, t) {
    let best = null;
    for (const s of data.syllables) if (s.start - 0.04 <= t) best = s;
    if (!best) return null;
    const gapEnd = best.end + 0.12;
    return t <= gapEnd ? best : null;
  }

  // ---- Pitch chart ----
  function drawRoll(ctx, data, t, s) {
    const R = ROLL;
    const px = (time) => R.playX + (time - t) * R.pxPerSec;
    ctx.save();
    ctx.beginPath();
    ctx.rect(R.x0, R.top, R.x1 - R.x0, 860);
    ctx.clip();
    ctx.fillStyle = "#1a2029";
    for (let g = Math.floor(t - 4); g < t + 7; g++) ctx.fillRect(px(g), R.top, 1, R.bottom - R.top);

    for (let i = 0; i < data.notes.length; i++) {
      const n = data.notes[i];
      const x0 = px(n.start), x1 = px(n.end);
      if (x1 < R.x0 || x0 > R.x1) continue;
      const y = noteY(n.midi);
      const active = t >= n.start && t < n.end;
      ctx.fillStyle = active ? "rgba(87,201,166,.45)" : "rgba(47,107,94,.45)";
      ctx.fillRect(x0, y - 14, Math.max(2, x1 - x0), 28);
      ctx.strokeStyle = active ? C.teal : "#3b7f6f";
      ctx.lineWidth = 1;
      ctx.strokeRect(x0 + 0.5, y - 13.5, Math.max(2, x1 - x0) - 1, 27);
    }
    for (const syl of data.syllables) {
      const n = data.notes[syl.first_note];
      if (!n) continue;
      const x = px(syl.start);
      if (x < R.x0 - 80 || x > R.x1 + 20) continue;
      text(ctx, syl.grapheme, x + 3, noteY(n.midi) - 22, `600 16px ${SANS}`, C.cream);
    }

    // Live pitch trace, up to the playhead only: stable near the note, deviating away from it.
    const midi = data.tracks.midi, dev = data.tracks.deviation, fps = data.meta.fps;
    const start = Math.max(1, Math.floor((t - 3.4) * fps));
    const end = Math.min(midi.length - 1, Math.floor(t * fps));
    ctx.lineWidth = 2.4;
    ctx.lineCap = "round";
    for (let i = start; i <= end; i++) {
      if (midi[i] == null || midi[i - 1] == null) continue;
      const stable = dev[i] != null && Math.abs(dev[i]) <= 30;
      ctx.strokeStyle = dev[i] == null ? C.cream : stable ? C.teal : C.red;
      ctx.beginPath();
      ctx.moveTo(px((i - 1) / fps), noteY(midi[i - 1]));
      ctx.lineTo(px(i / fps), noteY(midi[i]));
      ctx.stroke();
    }

    // Breath strip: voicing energy in gold, inhales in blue.
    const baseline = 906, height = 72;
    const energy = data.tracks.energy, inhale = data.tracks.inhale;
    const first = Math.max(0, Math.floor((t - 3.4) * fps));
    const last = Math.min(energy.length - 1, Math.ceil((t + 5.9) * fps));
    const area = (track, color) => {
      ctx.beginPath();
      ctx.moveTo(px(first / fps), baseline);
      for (let i = first; i <= last; i++) ctx.lineTo(px(i / fps), baseline - clamp(track[i], 0, 1) * height);
      ctx.lineTo(px(last / fps), baseline);
      ctx.closePath();
      ctx.fillStyle = color;
      ctx.fill();
    };
    area(energy, "#a97e39");
    area(inhale, "#4f94b8");

    // Phone timeline: vowels labelled, consonants as narrow dark cells.
    for (const p of data.phones) {
      const x0 = px(p.start), x1 = px(p.end);
      if (x1 < R.x0 || x0 > R.x1 || x1 - x0 < 1) continue;
      const active = t >= p.start && t < p.end;
      ctx.fillStyle = active ? "#7a5a26" : p.vowel ? "#1c232d" : "#262d38";
      ctx.fillRect(x0, 925, x1 - x0, 40);
      ctx.fillStyle = "#0d1117";
      ctx.fillRect(x1 - 1, 925, 1, 40);
      if (x1 - x0 > 14) text(ctx, p.ipa, (x0 + x1) / 2, 950, `13px ${MONO}`, active ? "#fff" : C.text, "center");
    }
    ctx.restore();

    ctx.fillStyle = "#d8d4c8";
    ctx.fillRect(R.playX, R.top, 1, 860);
    ctx.fillStyle = "rgba(240,176,74,.5)";
    ctx.fillRect(R.playX - 5, 925, 11, 40);
    if (s.midi != null) {
      ctx.beginPath();
      ctx.arc(R.playX, noteY(s.midi), 4, 0, Math.PI * 2);
      ctx.fillStyle = "#fff";
      ctx.fill();
    }
  }

  function prepare(data) {
    const flow = data.tracks.airflow, inhale = data.tracks.inhale;
    const phase = new Float64Array(flow.length);
    for (let i = 1; i < flow.length; i++) phase[i] = phase[i - 1] + (flow[i] * 1.0 + 0.12 * (flow[i] > 0.02) - inhale[i] * 1.0) / data.meta.fps;
    data.flowPhase = phase;
    data.syllables.forEach((s, i) => (s.index = i));
    for (const p of data.phones) {
      p.syllable = data.syllables.findIndex((s) => p.start >= s.start - 0.45 && p.start < s.end - 1e-4);
      if (p.syllable < 0) p.syllable = 0;
    }
    return data;
  }

  function sample(data, t) {
    const fps = data.meta.fps, tr = data.tracks;
    const x = clamp(t * fps, 0, tr.energy.length - 1.001);
    const i = Math.floor(x), k = x - i;
    const s = {};
    for (const key of [...ROWS, "energy", "inhale", "lung"]) s[key] = lerp(tr[key][i], tr[key][i + 1], k);
    s.midi = tr.midi[i];
    s.voiced = tr.voiced[i] > 0;
    return s;
  }

  function createDashboard(data, makeCanvas) {
    prepare(data);
    const staticLayer = makeCanvas(W, H);
    drawStatic(staticLayer.getContext("2d"));
    return function draw(ctx, t) {
      const s = sample(data, t);
      const phase = data.flowPhase[clamp(Math.floor(t * data.meta.fps), 0, data.flowPhase.length - 1)];
      const inhale = s.inhale;
      ctx.drawImage(staticLayer, 0, 0);
      const pitchPhase = t * 2 * Math.PI * 7;
      text(ctx, "VOCAL PATH", 24, 42, `700 24px ${SANS}`, C.cream);
      text(ctx, data.meta.subtitle, 196, 40, `13px ${MONO}`, C.text);
      text(ctx, "Notes extracted from the recording, not from a score  ·  Articulation and airflow are illustrative, not measured", 1896, 40, `13px ${SANS}`, C.text, "right");
      drawBody(ctx, data, s, phase);
      drawTract(ctx, s, phase, Math.max(s.airflow, s.voiced ? 0.2 : 0), inhale, s.airflow, pitchPhase);
      drawPhonation(ctx, data, s, t);
      drawRoll(ctx, data, t, s);
      // Timeline.
      const k = clamp(t / data.meta.duration, 0, 1), x = lerp(96, 1896, k);
      text(ctx, fmtTime(t), 24, 1050, `14px ${MONO}`, C.text);
      ctx.fillStyle = C.line;
      ctx.fillRect(96, 1046, 1800, 1);
      ctx.fillStyle = C.gold;
      ctx.fillRect(96, 1045, x - 96, 2);
      ctx.fillRect(x, 1039, 2, 14);
    };
  }

  return { createDashboard, W, H };
});
