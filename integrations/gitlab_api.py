"""GitLab API utilities for discovering package references and CI configs."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional, Set

import aiohttp

from core.logger import get_logger
from core.opsec import jitter

API_BASE = "https://gitlab.com/api/v4"


class GitLabAPI:
    """Minimal GitLab API wrapper."""

    def __init__(self, token: Optional[str] = None, base_url: str = API_BASE) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"PRIVATE-TOKEN": token} if token else {}
        self.log = get_logger(__name__)
        self.per_page = 100

    async def _get_json(
        self, session: aiohttp.ClientSession, url: str, **params: Any
    ) -> Any:
        await jitter(0.1, 0.3)
        self.log.debug("GET %s", url)
        async with session.get(url, headers=self.headers, params=params) as resp:
            if resp.status >= 400:
                self.log.warning("GitLab API error %s for %s", resp.status, url)
            return await resp.json()

    async def _paginate(self, session: aiohttp.ClientSession, url: str) -> List[Any]:
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

    async def list_projects(self, group: str) -> List[int]:
        """List project IDs for a group."""
        url = f"{self.base_url}/groups/{group}/projects"
        async with aiohttp.ClientSession() as session:
            data = await self._paginate(session, url)
            return [p.get("id") for p in data if "id" in p]

    async def fetch_file(self, project_id: int, path: str) -> Optional[str]:
        """Fetch a raw file from a GitLab project."""
        url = f"{self.base_url}/projects/{project_id}/repository/files/{path}/raw"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.text()
                return None

    async def search_packages(self, group: str) -> Set[str]:
        """Search projects for dependency names and config leaks."""
        projects = await self.list_projects(group)
        packages: Set[str] = set()
        for pid in projects:
            for filename in ("package.json", "requirements.txt"):
                content = await self.fetch_file(pid, filename)
                if content:
                    packages.update(self._parse_dependencies(content))
            for cfg in (".npmrc", ".pypirc", ".gitlab-ci.yml"):
                if await self.fetch_file(pid, cfg):
                    packages.add(cfg)
        return packages

    def _parse_dependencies(self, text: str) -> Set[str]:
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

    async def scan_group(self, group: str) -> Dict[str, Set[str]]:
        """High level helper returning packages and config leaks for a group."""
        pkgs = await self.search_packages(group)
        leaks: Set[str] = set()
        projects = await self.list_projects(group)
        for pid in projects:
            for cfg in (".npmrc", ".pypirc", ".gitlab-ci.yml"):
                if await self.fetch_file(pid, cfg):
                    leaks.add(f"{pid}:{cfg}")
        return {"packages": pkgs, "leaks": leaks}

