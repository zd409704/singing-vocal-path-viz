# Owner authorization — one-time GitHub upload of voice-mechanisms publication checkpoint

Date: 2026-11-09 17:29 Asia/Shanghai
From: Claude Manager (relayed owner decision)
To: Claude 4 / publication staging for singing-vocal-path-viz

## Decision

Owner authorizes uploading the current voice-mechanisms work to the existing repository https://github.com/zd409704/singing-vocal-path-viz ONLY. This supersedes the standing no-auto-push rule for this one upload.

Publication must be performed by the parent agent through the sanctioned CloudAgent path. This decision does not authorize the implementing Claude Code process, relay bots, or local git remotes to push.

## Scope of what may be published

A coherent lean publication checkpoint of current mechanisms plus the actual comparative A/B page/server and reproducible source/config/docs, taken at the next safe existing checkpoint boundary (mech-c3), without waiting for every remaining mechanism polish or for the in-flight numerical test suite to finish.

Keep the existing first-demo remote history intact. No force push, reset, or rebase. No destructive git. Do not commit the live working tree as-is; stage a curated tree.

## Hard omissions

Omit source-post audio/video/lyrics/reference; copyrighted covers; credentials and private operational logs; unrelated programs; target/, toolchains, binaries, caches; large generated snapshots and render WAVs unless a lean evidence summary is explicitly curated.

## Labels

Experimental and unvalidated features must be labelled. Unmet packet scope must be explicit. Implementation was still in progress when this snapshot was staged. This snapshot is publication staging only and is not owner quality acceptance. The staging-file sha256 before this public copy removed process details is 540f3db5f0def09069b340012f072022fe17fa6953f5b151b2865a8e373f2d3a.

## Record

This decision is recorded for audit. Staging artifacts live under results/voice_mechanisms/publish-stage-*/ and are for the parent CloudAgent upload step.

