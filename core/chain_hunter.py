"""Locate related organization accounts for chaining."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Dict, List, Union

from .recon_v2 import ReconEngineV2


class ChainHunter:
    """Hunt for related organization accounts and dependencies for chaining attacks."""

    def __init__(self, engine: ReconEngineV2 | None = None) -> None:
        self.engine = engine or ReconEngineV2()

    async def hunt(self, roots: Iterable[Union[str, Path]]) -> Dict[str, List[str]]:
        """Run full recon on provided roots (org names or paths) and return discovered packages."""
        results: Dict[str, List[str]] = {}
        for root in roots:
            packages = await self.engine.run([Path(root)])
            results[str(root)] = packages
        return results

    @staticmethod
    async def quick_hunt(org: str) -> List[str]:
        """Quickly guess related org accounts without full recon."""
        return [f"{org}-dev", f"{org}-ci"]


async def hunt(org: str) -> List[str]:
    """Convenience wrapper around :meth:`ChainHunter.quick_hunt`.

    Parameters
    ----------
    org:
        The organisation name to hunt for related accounts.
    """

    return await ChainHunter.quick_hunt(org)


__all__ = ["ChainHunter", "hunt"]
