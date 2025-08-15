"""Advanced recon engine with multi-source analysis."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict, List

import aiohttp
import base64
import json
import re

from .logger import get_logger
from .ml import predict_package_variants


@dataclass
class ReconResult:
    target: str
    packages: List[str]


class ReconEngineV2:
    def __init__(self, mode: str = "stealth") -> None:
        self.mode = mode
        self.log = get_logger(__name__)

    async def _github_search(self, session: aiohttp.ClientSession, term: str) -> List[str]:
        url = f"https://api.github.com/search/code?q={term}+filename:package.json"
        pkgs: List[str] = []
        try:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()
            for item in data.get("items", [])[:5]:
                try:
                    async with session.get(item["url"], timeout=10) as r2:
                        meta = await r2.json()
                    content = base64.b64decode(meta.get("content", "")).decode()
                    pkg = json.loads(content)
                    pkgs.extend(pkg.get("dependencies", {}).keys())
                except Exception:
                    continue
        except Exception as exc:  # pragma: no cover - network
            self.log.debug("github search failed: %s", exc)
        return pkgs

    async def _gitlab_search(self, session: aiohttp.ClientSession, term: str) -> List[str]:
        url = f"https://gitlab.com/api/v4/search?scope=blobs&search={term}"
        pkgs: List[str] = []
        try:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()
            for item in data[:5]:
                path = item.get("path", "")
                if path.endswith("requirements.txt"):
                    pkg = path.split("/")[-1].replace("requirements.txt", "").strip()
                    if pkg:
                        pkgs.append(pkg)
        except Exception as exc:  # pragma: no cover - network
            self.log.debug("gitlab search failed: %s", exc)
        return pkgs

    async def _search_repository(self, session: aiohttp.ClientSession, target: str) -> List[str]:
        base = target.split("//")[-1].split("/")[0]
        term = base.split(".")[0]
        gh, gl = await asyncio.gather(
            self._github_search(session, term),
            self._gitlab_search(session, term),
        )
        pkgs = gh + gl
        if not pkgs:
            pkgs.extend(predict_package_variants(term))
        return pkgs

    async def _query_registries(self, session: aiohttp.ClientSession, target: str) -> List[str]:
        base = target.split("//")[-1].split("/")[0]
        pkgs: List[str] = []
        url = f"https://registry.npmjs.org/-/v1/search?text={base}"
        try:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()
            for obj in data.get("objects", [])[:5]:
                pkgs.append(obj["package"]["name"])
        except Exception as exc:  # pragma: no cover - network
            self.log.debug("registry query failed: %s", exc)
        return pkgs

    async def _scrape(self, session: aiohttp.ClientSession, target: str) -> List[str]:
        self.log.debug("scraping %s", target)
        pkgs: List[str] = []
        try:
            async with session.get(target, timeout=10) as resp:
                text = await resp.text()
            for match in re.findall(r"([\w-]{3,})\.min\.js", text):
                pkgs.append(match)
        except Exception as exc:  # pragma: no cover - network
            self.log.debug("scrape failed: %s", exc)
        return pkgs

    async def run(self, targets: List[str]) -> List[ReconResult]:
        results: List[ReconResult] = []
        async with aiohttp.ClientSession() as session:
            for t in targets:
                pkgs: List[str] = []
                if self.mode == "aggressive":
                    pkgs.extend(await self._scrape(session, t))
                    pkgs.extend(await self._query_registries(session, t))
                repo_pkgs = await self._search_repository(session, t)
                pkgs.extend(repo_pkgs)
                results.append(ReconResult(target=t, packages=sorted(set(pkgs))))
        return results
