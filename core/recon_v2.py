"""Advanced recon engine with both multi-source network recon and local file scanning."""
from __future__ import annotations

import asyncio
import base64
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Iterable

import aiohttp

from .logger import get_logger
from .ml import predict_package_variants

log = get_logger(__name__)


@dataclass
class ReconResult:
    target: str
    packages: List[str]


class ReconEngineV2:
    def __init__(self, mode: str = "stealth") -> None:
        self.mode = mode

    # --- Online Recon Methods ---
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
        except Exception as exc:  # pragma: no cover
            log.debug("github search failed: %s", exc)
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
        except Exception as exc:  # pragma: no cover
            log.debug("gitlab search failed: %s", exc)
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
        except Exception as exc:  # pragma: no cover
            log.debug("registry query failed: %s", exc)
        return pkgs

    async def _scrape(self, session: aiohttp.ClientSession, target: str) -> List[str]:
        pkgs: List[str] = []
        try:
            async with session.get(target, timeout=10) as resp:
                text = await resp.text()
            for match in re.findall(r"([\w-]{3,})\.min\.js", text):
                pkgs.append(match)
        except Exception as exc:  # pragma: no cover
            log.debug("scrape failed: %s", exc)
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

    # --- Offline Recon Methods ---
    async def _scan_file(self, path: Path) -> Set[str]:
        try:
            text = path.read_text(errors="ignore")
        except Exception:  # pragma: no cover
            return set()
        return set(re.findall(r"[\w-]{2,}[/\\][\w-]{2,}|[\w-]+", text))

    async def _scan_path(self, root: Path) -> Set[str]:
        packages: Set[str] = set()
        for file in root.rglob("*"):
            if file.is_file():
                packages.update(await self._scan_file(file))
        return packages

    # --- Main Run ---
    async def run(self, targets: List[str | Path]) -> List[ReconResult]:
        results: List[ReconResult] = []
        async with aiohttp.ClientSession() as session:
            for t in targets:
                pkgs: Set[str] = set()
                if isinstance(t, Path) or t.startswith("file://") or Path(t).exists():
                    # Offline local scan
                    pkgs.update(await self._scan_path(Path(t)))
                else:
                    # Network recon
                    if self.mode == "aggressive":
                        pkgs.update(await self._scrape(session, t))
                        pkgs.update(await self._query_registries(session, t))
                    pkgs.update(await self._search_repository(session, t))
                # Predict variants
                all_pkgs = set()
                for p in pkgs:
                    all_pkgs.update(predict_package_variants(p))
                results.append(ReconResult(target=str(t), packages=sorted(all_pkgs)))
        return results


async def discover_packages(paths: Iterable[str | Path]) -> List[str]:
    """Wrapper for quick package discovery."""
    engine = ReconEngineV2()
    found: List[str] = []
    for r in await engine.run(paths):
        found.extend(r.packages)
    return sorted(set(found))


__all__ = ["ReconEngineV2", "ReconResult", "discover_packages"]
