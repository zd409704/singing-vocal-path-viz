# STATUS — singing-vocal-path-viz

state: DEMO_LANDED
next: Peter to watch the video with sound and judge whether the synthesized voice is acceptable, or supply a preferred public-domain or newly recorded adult clip.
updated: 2026-11-08 23:27 Asia/Shanghai (Claude Code)
human_lead: Peter

## Artifacts
- Material list, claims and limits: notes/MATERIAL.md
- How-to: docs/howto.md
- Method: notes/METHOD.md
- Demo audio source and license: notes/DEMO_AUDIO.md

## Key sha256
- results/vocal_path_demo.mp4: da1ec279026f04e9bdaefdc056b224359a018033d3bcb971f9f33ffc40b90baf
- results/vocal_path_demo.html: c4b41508ec4408faf08df6d2f13faec88aadbaa5556f795b5b98917b10b80f62
- assets/demo_audio/amazing_grace_synth.wav: eb216d8cc47ca20cff3ad3ff8b062fdbe4abfe9608d4b63f02651746fae9459a
- results/analysis.json: 8b50fd0a3d707f44122e29b18def0b93789e5e83916a33e5571f765aedf01105
- notes/MATERIAL.md: 535eb514f9f36d13d09b673115ebac581b4c3da4d4bfca0181bde80da305ecc8

## Manager next
- Decision: orch/decisions/2026-11-08-manager-start-reproduce-vocal-path.md
- Decision sha256: ca89d7cbe77bed48ece403ec9d8c96d558c196691c64801452ae4f030c9553ed
- Source post: https://x.com/slashui/status/2119421849134305644
- Visual reference: notes/reference/source-post-2119421849134305644.mp4 (layout only; soundtrack not used)

## Orchestrator
- Prompt: orch/prompts/REPRODUCE_VOCAL_PATH.txt
- Prompt sha256: 3e2ba59a7837dabb39264dd5c96453f9df4127d2953b42b39e3abc67ab0ead96
- PID: 420306
- Log: orch/logs/orch-reproduce-vocal-path-20261108-1016-EDT.log
- Model/effort: opus medium
- Audio rule: separately sourced public-domain or newly synthesized/recorded adult clip; do not extract the reference soundtrack
