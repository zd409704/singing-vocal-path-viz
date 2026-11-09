#!/usr/bin/env bash
# Build the chimera CLI from an unpacked source tree in this repository and install it
# at versions/<id>/chimera. Refuses checkpoints whose source is not vendored here.
# Usage: tools/vm/checkpoint.sh <mech-c3|upgraded-algo> [release|debug]
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
ID="${1:?version id (mech-c3 or upgraded-algo)}"
PROFILE="${2:-release}"
case "$ID" in
  mech-c3|upgraded-algo) ;;
  upstream-e939cf7)
    echo "upstream-e939cf7 is not vendored as engines/upstream-e939cf7." >&2
    echo "Run tools/vm/reconstruct_upstream.sh and build that tree. This script will not substitute upgraded-algo or mech-c3." >&2
    exit 1 ;;
  *)
    echo "refusing $ID: its source archive is omitted from this publication and is not replaced by another checkpoint." >&2
    exit 1 ;;
esac
case "$PROFILE" in
  release|debug) ;;
  *) echo "profile must be release or debug" >&2; exit 1 ;;
esac
SRC="$ROOT/engines/$ID"
[ -f "$SRC/Cargo.toml" ] || { echo "missing $SRC/Cargo.toml" >&2; exit 1; }
export RUSTUP_TOOLCHAIN="${RUSTUP_TOOLCHAIN:-stable}"
echo "Building $ID ($PROFILE) from $SRC with $(rustc --version)"
(cd "$SRC" && cargo build -p chimera-cli --profile "$PROFILE")
BIN="$SRC/target/$PROFILE/chimera"
[ -x "$BIN" ] || { echo "build did not produce $BIN" >&2; exit 1; }
mkdir -p "$ROOT/versions/$ID"
install -m 755 "$BIN" "$ROOT/versions/$ID/chimera"
python3 - "$ROOT/versions/$ID/SHA256SUMS" "$ROOT/versions/$ID/chimera" << 'PY'
import hashlib, sys
from pathlib import Path
sums, binary = Path(sys.argv[1]), Path(sys.argv[2])
expected = None
for line in sums.read_text().splitlines():
    if not line.strip():
        continue
    digest, name = line.split()
    if name == "chimera":
        expected = digest
got = hashlib.sha256(binary.read_bytes()).hexdigest()
print(f"built chimera sha256 {got}")
print(f"pinned release sha256 {expected}")
if got == expected:
    print("matches the omitted release binary hash")
else:
    print("does not match the omitted release binary hash; this is a local rebuild of the pinned source, not a prerecorded substitute")
PY
