"""PyPI package scanner with typo support."""
from __future__ import annotations

import aiohttp
from typing import Iterable, List, Set

from core.logger import get_logger
from modules import typo_variants

PYPI_URL = "https://pypi.org/pypi/{name}/json"

log = get_logger(__name__)


class Scanner:
    """Check for unclaimed PyPI packages."""

    def __init__(self, mirrors: Iterable[str] | None = None) -> None:
        self.mirrors = list(mirrors) if mirrors else [PYPI_URL]

    async def _exists(self, session: aiohttp.ClientSession, url_tpl: str, name: str) -> bool:
        url = url_tpl.format(name=name)
        try:
            resp = await session.get(url, timeout=10)
            return resp.status != 404
        except Exception as exc:  # pragma: no cover
            log.debug("mirror probe failed for %s: %s", url, exc)
            return True

    async def is_unclaimed(self, name: str) -> bool:
        async with aiohttp.ClientSession() as session:
            for mirror in self.mirrors:
                if await self._exists(session, mirror, name):
                    log.debug("%s found in mirror %s", name, mirror)
                    return False
        log.debug("%s is unclaimed", name)
        return True

    def generate_variants(self, package: str) -> Set[str]:
        return typo_variants(package)

    async def find_unclaimed(self, package: str) -> List[str]:
        names = {package} | self.generate_variants(package)
        results: List[str] = []
        for n in names:
            if await self.is_unclaimed(n):
                results.append(n)
        return results
