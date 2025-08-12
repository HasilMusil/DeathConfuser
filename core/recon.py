"""Reconnaissance utilities.

This module provides a lightweight recon engine that can perform simple
subdomain enumeration using passive services and scrape JavaScript files from
websites to extract potential package references.
"""

from __future__ import annotations

import asyncio
import json
import re
import shutil
from typing import Iterable, List, Set
from urllib.parse import urljoin

import aiohttp

from .logger import get_logger

SUBDOMAIN_API = "https://dns.bufferover.run/dns?q=.{}"
PACKAGE_RE = re.compile(r"(?:require\(['\"]|from ['\"])([\w@/\-]+)")
BUNDLE_IMPORT_RE = re.compile(r"[\w./-]+\\.js")


class Recon:
    """Simple asynchronous recon engine."""

    def __init__(self) -> None:
        self.log = get_logger(__name__)

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> str:
        try:
            async with session.get(url, timeout=10) as resp:
                return await resp.text()
        except Exception as exc:  # pragma: no cover - network errors
            self.log.debug(f"Failed to fetch {url}: {exc}")
            return ""

    async def enumerate_subdomains(self, domain: str) -> Set[str]:
        """Collect subdomains using passive DNS and external tools."""

        results: Set[str] = set()

        url = SUBDOMAIN_API.format(domain)
        async with aiohttp.ClientSession() as session:
            text = await self._fetch(session, url)
            try:
                data = json.loads(text)
                records: Iterable[str] = data.get("FDNS_A", [])
                for r in records:
                    if "," in r:
                        results.add(r.split(",")[1].strip())
            except json.JSONDecodeError:
                pass

        tool = shutil.which("subfinder") or shutil.which("amass")
        if tool:
            cmd = [tool, "-d", domain, "-silent"] if "subfinder" in tool else [tool, "enum", "-d", domain, "-silent"]
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                stdout, _ = await proc.communicate()
                for line in stdout.decode().splitlines():
                    if line:
                        results.add(line.strip())
            except Exception as exc:  # pragma: no cover - tool failure
                self.log.debug("subdomain tool failed: %s", exc)

        return results

    async def scrape_js(self, url: str) -> List[tuple[str, str]]:
        """Fetch scripts from a page and return discovered package references.

        Each returned tuple contains ``(package, code)``, where ``code`` is the
        JavaScript source (either inline or fetched from a remote script) that
        referenced the package. This snippet is passed to registry detection to
        prioritise which ecosystem to probe first.
        """

        seen: Set[str] = set()
        results: List[tuple[str, str]] = []
        async with aiohttp.ClientSession() as session:
            html = await self._fetch(session, url)
            s
