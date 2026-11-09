# Omissions from this publish staging archive

- source-post audio/video/lyrics/reference (including notes/reference/ and assets/demo_audio/source_post*)
- All WAV/MP4 renders and scratch/evidence audio
- Engine binaries (versions/*/chimera) and target/ build products
- Toolchains (.venv, rustup, cargo registry, bun-cache, node_modules)
- Large prechange snapshot results/voice_mechanisms/prechange-*
- orch/logs and private operational logs
- Live third_party/chimera-mech working tree (the publication uses the unpacked mech-c3 tree instead of mech-c3-source.tgz)
- upstream-e939cf7 / mech-c1 / mech-c2 full source.tgz (SHA256SUMS only in the staging archive). Upstream file contents are reconstructed in this git branch by reversing tools/chimera_voice_upgrade.patch; mech-c1 and mech-c2 are not
- The staging source tarballs themselves are not committed. Unpacked trees and SOURCE-FILES.sha256 manifests are
- Credentials, tokens, .env, private keys (none intentionally included)
- Unrelated local research programs outside this repository

