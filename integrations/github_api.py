"""GitHub API utilities for discovering package references and config leaks."""

from __future__ import annotations

import asyncio
import base64
import json
from typing import Any, Dict, Iterable, List, Optional, Set

import aiohttp

from ..core.logger import get_logger
from ..core.opsec import jitter

API_BASE = "https://api.github.com"


class GitHubAPI:
    """Wrapper around GitHub's REST API."""

    def __init__(self, token: Optional[str] = None, base_url: str = API_BASE) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"token {token}"} if token else {}
        self.log = get_logger(__name__)
        self.per_page = 100

    async def _get_json(
        self, session: aiohttp.ClientSession, url: str, **params: Any
    ) -> Any:
        """Perform a GET request and return parsed JSON with basic logging."""
        await jitter(0.1, 0.3)
        self.log.debug("GET %s", url)
        async with session.get(url, headers=self.headers, params=params) as resp:
            if resp.status >= 400:
                self.log.warning("GitHub API error %s for %s", resp.status, url)
            return await resp.json()

    async def _paginate(self, session: aiohttp.ClientSession, url: str) -> List[Any]:
        """Return full list of paginated results."""
        results: List[Any] = []
        page = 1
        while True:
            data = await self._get_json(session, url, per_page=self.per_page, page=page)
            if not isinstance(data, list) or not data:
                break
            results.extend(data)
            if len(data) < self.per_page:
                break
            page += 1
        return results

    async def list_repos(self, org: str) -> List[str]:
        """Return repositories for an organization/user."""
        url = f"{self.base_url}/orgs/{org}/repos"
        async with aiohttp.ClientSession() as session:
            data = await self._paginate(session, url)
            return [r.get("full_name") for r in data if "full_name" in r]

    async def fetch_file(self, repo: str, path: str) -> Optional[str]:
        """Fetch a file from a repository if it exists."""
        url = f"{self.base_url}/repos/{repo}/contents/{path}"
        async with aiohttp.ClientSession() as session:
            data = await self._get_json(session, url)
            if not isinstance(data, dict):
                return None
            content = data.get("content")
            if not content:
                return None
            try:
                return base64.b64decode(content).decode()
            except Exception:  # pragma: no cover - decode issues
                return None

    async def search_packages(self, org: str) -> Set[str]:
        """Search repositories for dependency names and leaked configs."""
        repos = await self.list_repos(org)
        packages: Set[str] = set()
        for repo in repos:
            for filename in ("package.json", "requirements.txt"):
                content = await self.fetch_file(repo, filename)
                if content:
                    packages.update(self._parse_dependencies(content))
            for cfg in (".npmrc", ".pypirc"):
                if await self.fetch_file(repo, cfg):
                    packages.add(cfg)
        return packages

    async def dork(self, query: str, pages: int = 1) -> List[Dict[str, Any]]:
        """Run a GitHub search code query (dork) and return results."""
        results: List[Dict[str, Any]] = []
        async with aiohttp.ClientSession() as session:
            for page in range(1, pages + 1):
                params = {"q": query, "per_page": self.per_page, "page": page}
                data = await self._get_json(session, f"{self.base_url}/search/code", **params)
                if isinstance(data, dict):
                    items = data.get("items", [])
                    results.extend(items)
                    if len(items) < self.per_page:
                        break
                else:
                    break
        self.log.info("Dork query '%s' returned %d items", query, len(results))
        return results

    def _parse_dependencies(self, text: str) -> Set[str]:
        """Extract package names from manifest text."""
        try:
            data = json.loads(text)
            deps = data.get("dependencies") or {}
            if isinstance(deps, dict):
                return set(deps.keys())
        except json.JSONDecodeError:
            pass

        pkgs: Set[str] = set()
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
            if name:
                pkgs.add(name)
        return pkgs

    async def scan_org(self, org: str) -> Dict[str, Set[str]]:
        """High level helper returning packages and config leaks for ``org``."""
        packages = await self.search_packages(org)
        leaks: Set[str] = set()
        repos = await self.list_repos(org)
        for repo in repos:
            for cfg in (".npmrc", ".pypirc"):
                content = await self.fetch_file(repo, cfg)
                if content:
                    leaks.add(f"{repo}:{cfg}")
        return {"packages": packages, "leaks": leaks}

