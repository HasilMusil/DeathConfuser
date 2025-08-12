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
        referenced the package.  This snippet is passed to registry detection to
        prioritise which ecosystem to probe first.
        """

        seen: Set[str] = set()
        results: List[tuple[str, str]] = []
        async with aiohttp.ClientSession() as session:
            html = await self._fetch(session, url)
            srcs = re.findall(r'<script[^>]+src=["\'](.*?)["\']', html)
            inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.S)

            for script in inline_scripts:
                pkgs = self._extract_packages(script) | self._extract_bundle_imports(script)
                for pkg in pkgs:
                    if pkg not in seen:
                        seen.add(pkg)
                        # include script context for detect_registry()
                        results.append((pkg, script))

            for src in srcs:
                js_url = urljoin(url, src)
                js = await self._fetch(session, js_url)
                pkgs = self._extract_packages(js) | self._extract_bundle_imports(js)
                for pkg in pkgs:
                    if pkg not in seen:
                        seen.add(pkg)
                        # provide code context for detect_registry()
                        results.append((pkg, js))

        return sorted(results, key=lambda x: x[0])

    def _extract_packages(self, text: str) -> Set[str]:
        return set(PACKAGE_RE.findall(text))

    def _extract_bundle_imports(self, text: str) -> Set[str]:
        """Attempt to pull module names from bundled JavaScript."""
        imports: Set[str] = set()
        if "webpack" in text:
            for match in BUNDLE_IMPORT_RE.findall(text):
                if "node_modules" in match:
                    pkg = match.split("node_modules/")[-1].split("/")[0]
                    if pkg:
                        imports.add(pkg)
        return imports

    async def github_dorks(self, term: str) -> List[str]:
        """Search GitHub for leaked configuration files matching term."""
        url = f"https://api.github.com/search/code?q={term}+filename:.npmrc"
        async with aiohttp.ClientSession() as session:
            text = await self._fetch(session, url)
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                return []
            items = data.get("items", [])
            return [item.get("html_url", "") for item in items]

    async def pastebin_search(self, term: str) -> List[str]:
        """Search Pastebin dumps for occurrences of ``term``."""
        url = f"https://psbdmp.ws/api/search/{term}"
        async with aiohttp.ClientSession() as session:
            text = await self._fetch(session, url)
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                return []
            pastes = data.get("data", [])
            return [f"https://pastebin.com/{p['id']}" for p in pastes if 'id' in p]

