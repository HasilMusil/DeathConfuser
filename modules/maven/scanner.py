"""Maven Central artifact scanner."""
from __future__ import annotations

import aiohttp
from typing import List, Set

from ...core.logger import get_logger
from .. import typo_variants

SEARCH_URL = "https://search.maven.org/solrsearch/select?q=g:%22{group}%22+AND+a:%22{artifact}%22&rows=1&wt=json"

log = get_logger(__name__)


class Scanner:
    """Check for unclaimed Maven artifacts."""

    async def is_unclaimed(self, group: str, artifact: str) -> bool:
        url = SEARCH_URL.format(group=group, artifact=artifact)
        async with aiohttp.ClientSession() as session:
            try:
                resp = await session.get(url, timeout=10)
                if resp.status != 200:
                    return False
                data = await resp.json()
            except Exception as exc:  # pragma: no cover
                log.debug("search failed: %s", exc)
                return False
        found = data.get("response", {}).get("numFound", 0) > 0
        if found:
            log.debug("artifact %s:%s exists", group, artifact)
        else:
            log.debug("artifact %s:%s is unclaimed", group, artifact)
        return not found

    def generate_variants(self, artifact: str) -> Set[str]:
        return typo_variants(artifact)

    async def find_unclaimed(self, group: str, artifact: str) -> List[str]:
        names = {artifact} | self.generate_variants(artifact)
        results: List[str] = []
        for name in names:
            if await self.is_unclaimed(group, name):
                results.append(name)
        return results
