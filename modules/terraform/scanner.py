"""Terraform module scanner with domain inference."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, List, Set

import aiohttp

from ...core.logger import get_logger
from .. import typo_variants

TERRAFORM_URL = "https://registry.terraform.io/v1/modules/{path}"

log = get_logger(__name__)


class Scanner:
    """Check for unclaimed Terraform modules."""

    def __init__(self, api_url: str = TERRAFORM_URL) -> None:
        self.api_url = api_url

    async def _exists(self, session: aiohttp.ClientSession, path: str) -> bool:
        url = self.api_url.format(path=path)
        try:
            resp = await session.get(url, timeout=10)
            return resp.status != 404
        except Exception as exc:  # pragma: no cover - network
            log.debug("terraform probe failed for %s: %s", path, exc)
            return True

    async def is_unclaimed(self, path: str) -> bool:
        async with aiohttp.ClientSession() as session:
            if await self._exists(session, path):
                log.debug("%s exists", path)
                return False
        log.debug("%s is unclaimed", path)
        return True

    def _infer_from_domain(self, org: str) -> Set[str]:
        parts = org.split(".")
        hints = {f"{org}/{part}/module" for part in parts if part}
        return hints

    def generate_candidates(self, module: str) -> Set[str]:
        domain = module.split("/")[0]
        return {module} | typo_variants(module) | self._infer_from_domain(domain)

    async def find_unclaimed(self, module: str) -> List[str]:
        candidates = self.generate_candidates(module)
        results: List[str] = []
        for m in candidates:
            if await self.is_unclaimed(m):
                results.append(m)
        return results

