#!/usr/bin/env node
// Render analysis.json to a synced MP4, or single preview PNGs with --still.
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");
const { createCanvas, GlobalFonts } = require("@napi-rs/canvas");
const { createDashboard, W, H } = require("./dashboard.js");

const FONT_ROOT = "/usr/share/fonts/truetype/sand-box/google";
const FONTS = [
  [`${FONT_ROOT}/IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf`, "IBM Plex Sans"],
  [`${FONT_ROOT}/IBM Plex Mono/IBMPlexMono-Regular.ttf`, "IBM Plex Mono"],
  [`${FONT_ROOT}/IBM Plex Mono/IBMPlexMono-SemiBold.ttf`, "IBM Plex Mono"],
];

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : fallback;
}

async function main() {
  for (const [file, family] of FONTS) if (fs.existsSync(file)) GlobalFonts.registerFromPath(file, family);
  const data = JSON.parse(fs.readFileSync(arg("data", "results/analysis.json"), "utf8"));
  const canvas = createCanvas(W, H);
  const ctx = canvas.getContext("2d");
  const draw = createDashboard(data, (w, h) => createCanvas(w, h));

  const still = arg("still");
  if (still) {
    const outDir = arg("outdir", "results/preview");
    fs.mkdirSync(outDir, { recursive: true });
    for (const t of still.split(",").map(Number)) {
      draw(ctx, t);
      fs.writeFileSync(path.join(outDir, `frame_${String(t).padStart(5, "0")}.png`), canvas.toBuffer("image/png"));
    }
    return;
  }

  const fps = Number(arg("fps", "30"));
  const out = arg("out", "results/vocal_path_demo.mp4");
  const audio = arg("audio");
  const frames = Math.ceil(data.meta.duration * fps);
  const ffmpeg = spawn("ffmpeg", ["-y", "-loglevel", "error",
    "-f", "rawvideo", "-pix_fmt", "rgba", "-s", `${W}x${H}`, "-r", String(fps), "-i", "-",
    "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
    { stdio: ["pipe", "inherit", "inherit"] });
  const done = new Promise((resolve, reject) => ffmpeg.on("close", (c) => (c ? reject(new Error(`ffmpeg exit ${c}`)) : resolve())));
  for (let f = 0; f < frames; f++) {
    draw(ctx, f / fps);
    const buf = Buffer.from(ctx.getImageData(0, 0, W, H).data.buffer);
    if (!ffmpeg.stdin.write(buf)) await new Promise((r) => ffmpeg.stdin.once("drain", r));
    if (f % 150 === 0) console.log(`frame ${f}/${frames}`);
  }
  ffmpeg.stdin.end();
  await done;
  console.log(`wrote ${out}`);
}

main().catch((e) => { console.error(e); process.exit(1); });
