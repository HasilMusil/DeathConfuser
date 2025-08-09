"""NPM package scanner with typo generation and registry probing."""
from __future__ import annotations

import aiohttp
from typing import Iterable, List, Set

from core.logger import get_logger
from modules import typo_variants

NPM_REGISTRY = "https://registry.npmjs.org"

log = get_logger(__name__)


class Scanner:
    """Check for unclaimed NPM packages across registries."""

    def __init__(self, registries: Iterable[str] | None = None) -> None:
        self.registries = list(registries) if registries else [NPM_REGISTRY]

    async def _exists(self, session: aiohttp.ClientSession, registry: str, name: str) -> bool:
        url = f"{registry.rstrip('/')}/{name}"
        try:
            resp = await session.get(url, timeout=10)
            return resp.status != 404
        except Exception as exc:  # pragma: no cover - network
            log.debug("registry probe failed for %s: %s", url, exc)
            return True

    async def is_unclaimed(self, name: str) -> bool:
        async with aiohttp.ClientSession() as session:
            for reg in self.registries:
                if await self._exists(session, reg, name):
                    log.debug("%s found in %s", name, reg)
                    return False
        log.debug("%s is unclaimed", name)
        return True

    def generate_variants(self, package: str) -> Set[str]:
        return typo_variants(package)

    async def find_unclaimed(self, package: str) -> List[str]:
        candidates = {package} | self.generate_variants(package)
        results: List[str] = []
        for name in candidates:
            if await self.is_unclaimed(name):
                results.append(name)
        return results
