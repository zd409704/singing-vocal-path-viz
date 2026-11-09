#!/usr/bin/env bash
# Reconstruct upstream snapshot e939cf7 from this repository, without a vendored second copy
# and without using the mech-c3 tree.
# The result is file-identical to public commit e939cf733f7bbaed9e5698a242b1161dc9580679
# (verified when this publication was prepared) and to versions/upstream-e939cf7/SOURCE-FILES.sha256.
# Usage: tools/vm/reconstruct_upstream.sh [dest]
# Default dest: versions/upstream-e939cf7/source (gitignored). Refuses to overwrite.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
DEST="${1:-$ROOT/versions/upstream-e939cf7/source}"
if [ -e "$DEST" ]; then
  echo "refusing to overwrite $DEST" >&2
  exit 1
fi
mkdir -p "$(dirname "$DEST")"
cp -a "$ROOT/engines/upgraded-algo" "$DEST"
rm -rf "$DEST/target"
patch -R -p1 -d "$DEST" < "$ROOT/tools/chimera_voice_upgrade.patch"
python3 - "$DEST" "$ROOT/versions/upstream-e939cf7/SOURCE-FILES.sha256" << 'PY'
import hashlib, sys
from pathlib import Path
root, man = Path(sys.argv[1]), Path(sys.argv[2])
expected = {}
for line in man.read_text().splitlines():
    if not line.strip():
        continue
    digest, rel = line.split(None, 1)
    expected[rel] = digest
disk = {}
for p in root.rglob("*"):
    if not p.is_file():
        continue
    rel = p.relative_to(root).as_posix()
    if rel.split("/", 1)[0] == "target":
        continue
    disk[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
missing = sorted(set(expected) - set(disk))
extra = sorted(set(disk) - set(expected))
bad = sorted(k for k in expected if k in disk and disk[k] != expected[k])
if missing or extra or bad:
    print(f"upstream reconstruct mismatch missing={len(missing)} extra={len(extra)} bad={len(bad)}", file=sys.stderr)
    for item in (missing[:8] + extra[:8] + bad[:8]):
        print(" ", item, file=sys.stderr)
    sys.exit(1)
print(f"upstream source matches {len(expected)} file hashes")
PY
echo "Tree is at $DEST"
echo "Provenance: https://github.com/jamesondh/chimera-vocal-synth/commit/e939cf733f7bbaed9e5698a242b1161dc9580679"
echo "Build: (cd \"$DEST\" && cargo build -p chimera-cli --release)"
echo "Install: install -m 755 \"$DEST/target/release/chimera\" \"$ROOT/versions/upstream-e939cf7/chimera\""
echo "mech-c1 and mech-c2 cannot be reconstructed from this repository."
