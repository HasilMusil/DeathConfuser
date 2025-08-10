"""NuGet package scanner with typo variants."""
from __future__ import annotations

import aiohttp
from typing import List, Set

from ...core.logger import get_logger
from .. import typo_variants

NUGET_URL = "https://api.nuget.org/v3/registration5-semver1/{name}/index.json"

log = get_logger(__name__)


class Scanner:
    """Check for unclaimed NuGet packages."""

    async def is_unclaimed(self, name: str) -> bool:
        url = NUGET_URL.format(name=name.lower())
        async with aiohttp.ClientSession() as session:
            try:
                resp = await session.get(url, timeout=10)
                if resp.status == 404:
                    log.debug("%s is unclaimed", name)
                    return True
                return resp.status == 404
            except Exception as exc:  # pragma: no cover
                log.debug("nuget probe failed: %s", exc)
                return False

    def generate_variants(self, package: str) -> Set[str]:
        return typo_variants(package)

    async def find_unclaimed(self, package: str) -> List[str]:
        names = {package} | self.generate_variants(package)
        results: List[str] = []
        for n in names:
            if await self.is_unclaimed(n):
                results.append(n)
        return results
