"""Go module scanner leveraging proxy.golang.org and local hints."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, List, Set

import aiohttp

from ...core.logger import get_logger
from .. import typo_variants

GOPROXY_URL = "https://proxy.golang.org/{module}/@v/list"

log = get_logger(__name__)


class Scanner:
    """Check for unclaimed Go modules via Go proxy."""

    def __init__(self, proxy_url: str = GOPROXY_URL) -> None:
        self.proxy_url = proxy_url

    async def _exists(self, session: aiohttp.ClientSession, module: str) -> bool:
        url = self.proxy_url.format(module=module)
        try:
            resp = await session.get(url, timeout=10)
            if resp.status == 200:
                text = await resp.text()
                return bool(text.strip())
            return resp.status != 404
        except Exception as exc:  # pragma: no cover - network
            log.debug("go proxy error for %s: %s", module, exc)
            return True

    async def is_unclaimed(self, module: str) -> bool:
        async with aiohttp.ClientSession() as session:
            if await self._exists(session, module):
                log.debug("%s exists", module)
                return False
        log.debug("%s is unclaimed", module)
        return True

    def _local_hints(self) -> Set[str]:
        hints: Set[str] = set()
        gomod = Path("go.mod")
        if gomod.exists():
            for line in gomod.read_text().splitlines():
                if line.startswith("module "):
                    hints.add(line.split()[1])
        return hints

    def generate_candidates(self, module: str) -> Set[str]:
        return {module} | typo_variants(module) | self._local_hints()

    async def find_unclaimed(self, module: str) -> List[str]:
        candidates = self.generate_candidates(module)
        results: List[str] = []
        for m in candidates:
            if await self.is_unclaimed(m):
                results.append(m)
        return results

