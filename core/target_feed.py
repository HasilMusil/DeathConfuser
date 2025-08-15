"""Automatic target retrieval from bug bounty platforms."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import List, Dict

import aiohttp

from .logger import get_logger
from .ml import score_target_priority

log = get_logger(__name__)

H1_API = "https://hackerone.com/directory/programs/search"  # placeholder
BC_API = "https://bugcrowd.com/programs.json"  # placeholder
KNOWN_TECHS = {"npm", "pypi", "golang", "maven", "docker"}


async def _fetch_json(session: aiohttp.ClientSession, url: str) -> List[Dict[str, object]]:
    """Helper to fetch JSON data with graceful error handling."""
    try:
        async with session.get(url, timeout=20) as resp:  # pragma: no cover - network
            if resp.content_type == "application/json":
                return await resp.json()  # type: ignore[return-value]
            text = await resp.text()
            log.debug("non-JSON response from %s: %s", url, text[:100])
    except Exception as exc:  # pragma: no cover - offline
        log.debug("target feed fetch failed for %s: %s", url, exc)
    return []


async def fetch_targets() -> List[str]:
    """Fetch bounty targets from HackerOne and Bugcrowd."""
    async with aiohttp.ClientSession() as session:
        h1_data, bc_data = await asyncio.gather(
            _fetch_json(session, H1_API),
            _fetch_json(session, BC_API),
        )
    targets: List[str] = []
    for item in h1_data:
        scope = item.get("in_scope") or item.get("offers_bounties")
        techs = {t.lower() for t in item.get("tech", [])}
        if scope and techs.intersection(KNOWN_TECHS):
            url = item.get("url") or item.get("website")
            if url:
                targets.append(str(url))
    for item in bc_data:
        scope = item.get("status") == "active" or item.get("target_group") == "in_scope"
        techs = {t.lower() for t in item.get("categories", [])}
        if scope and techs.intersection(KNOWN_TECHS):
            url = item.get("target") or item.get("url")
            if url:
                targets.append(str(url))
    uniq = sorted(set(targets))
    return sorted(uniq, key=score_target_priority, reverse=True)


async def update_target_file(path: str | Path) -> Path:
    """Retrieve targets and persist them to ``path``."""
    target_path = Path(path)
    targets = await fetch_targets()
    if targets:
        target_path.write_text("\n".join(targets) + "\n")
        log.info("Wrote %s targets to %s", len(targets), target_path)
    else:
        log.debug("no targets retrieved; existing file preserved")
    return target_path


__all__ = ["fetch_targets", "update_target_file"]

async def update_target_file(path: str | Path) -> Path:
    """Retrieve targets and persist them to ``path``."""
    target_path = Path(path)
    targets = await fetch_targets()
    if targets:
        target_path.write_text("\n".join(targets) + "\n")
        log.info("Wrote %s targets to %s", len(targets), target_path)
    else:
        log.debug("no targets retrieved; existing file preserved")
    return target_path
