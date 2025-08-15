"""Repeatedly recon related organisations."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, Dict, List

from .recon_v2 import ReconEngineV2


class ChainHunter:
    def __init__(self, engine: ReconEngineV2 | None = None) -> None:
        self.engine = engine or ReconEngineV2()

    async def hunt(self, roots: Iterable[str | Path]) -> Dict[str, List[str]]:
        results: Dict[str, List[str]] = {}
        for root in roots:
            packages = await self.engine.run([Path(root)])
            results[str(root)] = packages
        return results


__all__ = ["ChainHunter"]
