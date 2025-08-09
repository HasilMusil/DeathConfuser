"""Crates.io package scanner with local Cargo hints."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, List, Set

import aiohttp

from core.logger import get_logger
from modules import typo_variants

CRATES_URL = "https://crates.io/api/v1/crates/{name}"

log = get_logger(__name__)


class Scanner:
    """Check for unclaimed Rust crates."""

    def __init__(self, api_url: str = CRATES_URL) -> None:
        self.api_url = api_url

    async def _exists(self, session: aiohttp.ClientSession, crate: str) -> bool:
        url = self.api_url.format(name=crate)
        try:
            resp = await session.get(url, timeout=10)
            return resp.status != 404
        except Exception as exc:  # pragma: no cover - network
            log.debug("crate probe failed for %s: %s", crate, exc)
            return True

    async def is_unclaimed(self, name: str) -> bool:
        async with aiohttp.ClientSession() as session:
            if await self._exists(session, name):
                log.debug("%s exists", name)
                return False
        log.debug("%s is unclaimed", name)
        return True

    def _local_hints(self) -> Set[str]:
        hints: Set[str] = set()
        cargo = Path("Cargo.toml")
        if cargo.exists():
            for line in cargo.read_text().splitlines():
                if line.strip().startswith("name"):
                    hints.add(line.split("=")[1].strip().strip('"'))
        return hints

    def generate_candidates(self, crate: str) -> Set[str]:
        return {crate} | typo_variants(crate) | self._local_hints()

    async def find_unclaimed(self, crate: str) -> List[str]:
        candidates = self.generate_candidates(crate)
        results: List[str] = []
        for c in candidates:
            if await self.is_unclaimed(c):
                results.append(c)
        return results

