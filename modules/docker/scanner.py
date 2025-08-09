"""Docker Hub scanner with local hints."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Iterable, List, Set

import aiohttp

from core.logger import get_logger
from modules import typo_variants

DOCKER_URL = "https://hub.docker.com/v2/repositories/{repo}/"

log = get_logger(__name__)


class Scanner:
    """Check for unclaimed Docker Hub repositories."""

    def __init__(self, api_url: str = DOCKER_URL) -> None:
        self.api_url = api_url

    async def _exists(self, session: aiohttp.ClientSession, repo: str) -> bool:
        url = self.api_url.format(repo=repo)
        try:
            resp = await session.get(url, timeout=10)
            return resp.status != 404
        except Exception as exc:  # pragma: no cover - network
            log.debug("docker probe failed for %s: %s", repo, exc)
            return True

    async def is_unclaimed(self, repo: str) -> bool:
        async with aiohttp.ClientSession() as session:
            if await self._exists(session, repo):
                log.debug("%s exists", repo)
                return False
        log.debug("%s is unclaimed", repo)
        return True

    def _local_hints(self) -> Set[str]:
        hints: Set[str] = set()
        docker_cfg = Path.home() / ".docker" / "config.json"
        if docker_cfg.exists():
            try:
                data = json.loads(docker_cfg.read_text())
                hints.update(data.get("auths", {}).keys())
            except Exception:  # pragma: no cover - malformed json
                pass
        return hints

    def generate_candidates(self, repo: str) -> Set[str]:
        base = repo.split(":")[0]
        return {base} | typo_variants(base) | self._local_hints()

    async def find_unclaimed(self, repo: str) -> List[str]:
        candidates = self.generate_candidates(repo)
        results: List[str] = []
        for r in candidates:
            if await self.is_unclaimed(r):
                results.append(r)
        return results

