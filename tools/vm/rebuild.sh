#!/usr/bin/env bash
# Rebuild the two vendored engines. The page planner uses upgraded-algo; mech renders use mech-c3.
# Usage: tools/vm/rebuild.sh [release|debug]
set -euo pipefail
DIR=$(cd "$(dirname "$0")" && pwd)
PROFILE="${1:-release}"
"$DIR/checkpoint.sh" upgraded-algo "$PROFILE"
"$DIR/checkpoint.sh" mech-c3 "$PROFILE"
