"""Resolve chimera binaries for checkpoints this publication can actually build.

upgraded-algo and mech-c3 are unpacked under engines/. upstream-e939cf7 is obtained
by reversing tools/chimera_voice_upgrade.patch, then building that tree. mech-c1 and
mech-c2 stay unavailable: their archives were omitted and are not replaced by mech-c3.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AVAIL = json.loads((ROOT / "versions/availability.json").read_text())


def checkpoint_info(checkpoint):
    try:
        return AVAIL["checkpoints"][checkpoint]
    except KeyError as e:
        raise KeyError(f"unknown checkpoint {checkpoint}") from e


def engine_binary(checkpoint):
    """Return the built chimera for this checkpoint only. Never a different checkpoint."""
    info = checkpoint_info(checkpoint)
    pinned = ROOT / "versions" / checkpoint / "chimera"
    if pinned.is_file():
        return pinned
    src = info.get("sourceTree")
    if src:
        for profile in ("release", "debug"):
            cand = ROOT / src / "target" / profile / "chimera"
            if cand.is_file():
                return cand
    reason = info.get("reason") or "no source in this publication"
    raise FileNotFoundError(
        f"no chimera binary for checkpoint {checkpoint}. {reason} "
        "This server does not substitute a different checkpoint."
    )
