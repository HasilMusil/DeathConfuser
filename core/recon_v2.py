"""Recon engine v2 implementing light-weight async scanners.

This module purposely keeps the implementation simple while mimicking the
behaviour of the far more feature rich engine described in the upgrade
plan.  It discovers package names in source repositories and predicts
possible private variants using the :mod:`DeathConfuser.core.ml` helper.
"""
from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Iterable, List, Set

from .ml import predict_package_variants
from .logger import get_logger

log = get_logger(__name__)


class ReconEngineV2:
    """Find package names in repositories and related domains."""

    def __init__(self, mode: str = "stealth") -> None:
        self.mode = mode

    async def _scan_file(self, path: Path) -> Set[str]:
        try:
            text = path.read_text(errors="ignore")
        except Exception:  # pragma: no cover - binary file
            return set()
        # extremely small regex looking for package references
        hits = set(re.findall(r"[\w-]{2,}[/\\][\w-]{2,}|[\w-]+", text))
        return hits

    async def _scan_path(self, root: Path) -> Set[str]:
        packages: Set[str] = set()
        for file in root.rglob("*"):
            if file.is_file():
                packages.update(await self._scan_file(file))
        return packages

    async def run(self, roots: Iterable[Path]) -> List[str]:
        """Asynchronously scan ``roots`` for package names."""

        tasks = [self._scan_path(Path(r)) for r in roots]
        found: Set[str] = set()
        for pkg_set in await asyncio.gather(*tasks):
            for name in pkg_set:
                found.update(predict_package_variants(name))
        return sorted(found)


async def discover_packages(paths: Iterable[str | Path]) -> List[str]:
    """Convenience wrapper used by CLI/API/WebUI."""

    engine = ReconEngineV2()
    return await engine.run([Path(p) for p in paths])


__all__ = ["ReconEngineV2", "discover_packages"]
