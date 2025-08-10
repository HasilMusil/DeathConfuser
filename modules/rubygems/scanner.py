"""RubyGems package scanner with typo support and local hints."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, List, Set

import aiohttp

from ...core.logger import get_logger
from .. import typo_variants

RUBYGEMS_URL = "https://rubygems.org/api/v1/gems/{name}.json"

log = get_logger(__name__)


class Scanner:
    """Check for unclaimed RubyGems packages across sources."""

    def __init__(self, sources: Iterable[str] | None = None) -> None:
        self.sources = list(sources) if sources else [RUBYGEMS_URL]

    async def _exists(self, session: aiohttp.ClientSession, url: str) -> bool:
        try:
            resp = await session.get(url, timeout=10)
            return resp.status != 404
        except Exception as exc:  # pragma: no cover - network errors
            log.debug("rubygems probe failed for %s: %s", url, exc)
            return True

    async def is_unclaimed(self, name: str) -> bool:
        async with aiohttp.ClientSession() as session:
            for src in self.sources:
                url = src.format(name=name)
                if await self._exists(session, url):
                    log.debug("%s found in %s", name, src)
                    return False
        log.debug("%s is unclaimed", name)
        return True

    def _local_hints(self) -> Set[str]:
        hints: Set[str] = set()
        gemrc = Path.home() / ".gemrc"
        if gemrc.exists():
            for line in gemrc.read_text().splitlines():
                if "sources" in line:
                    hints.update(p.rsplit("/", 1)[-1] for p in line.split())
        return hints

    def generate_candidates(self, package: str) -> Set[str]:
        return {package} | typo_variants(package) | self._local_hints()

    async def find_unclaimed(self, package: str) -> List[str]:
        candidates = self.generate_candidates(package)
        results: List[str] = []
        for name in candidates:
            if await self.is_unclaimed(name):
                results.append(name)
        return results

