#!/usr/bin/env bash
# Check vendored engine trees against the file manifests taken from the pinned source archives.
# Does not require the omitted tarballs or binaries.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
python3 - "$ROOT" << 'PY'
import hashlib, sys
from pathlib import Path
root = Path(sys.argv[1])
pairs = [
    (root / "engines/upgraded-algo", root / "versions/upgraded-algo/SOURCE-FILES.sha256"),
    (root / "engines/mech-c3", root / "versions/mech-c3/SOURCE-FILES.sha256"),
]
failed = False
for tree, man in pairs:
    expected = {}
    for line in man.read_text().splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(None, 1)
        expected[rel] = digest
    disk = {}
    for p in tree.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(tree).as_posix()
        if rel.split("/", 1)[0] == "target":
            continue
        disk[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    missing = sorted(set(expected) - set(disk))
    extra = sorted(k for k in disk if k not in expected)
    bad = sorted(k for k in expected if k in disk and disk[k] != expected[k])
    status = "ok" if not (missing or extra or bad) else "MISMATCH"
    if status != "ok":
        failed = True
    print(f"{status} {tree.relative_to(root)} files={len(disk)} manifest={len(expected)} missing={len(missing)} extra={len(extra)} bad={len(bad)}")
if failed:
    sys.exit(1)
print("vendored sources match the pinned archive file manifests")
PY
