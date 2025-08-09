"""Simulate publishing NPM packages with optional real execution."""
from __future__ import annotations

import asyncio
import random
import shutil

from core.logger import get_logger
from modules.npm.scanner import Scanner
from opsec import load_profiles
from utils.fs_utils import temporary_directory

log = get_logger(__name__)


async def publish(name: str, payload: str, registry: str = "https://registry.npmjs.org", dry_run: bool = True) -> None:
    """Publish ``payload`` if the package ``name`` is unclaimed."""

    scanner = Scanner([registry])
    if not await scanner.is_unclaimed(name):
        log.info("Package %s already exists", name)
        return

    profile = random.choice(load_profiles()) if load_profiles() else {"name": "test", "email": "test@example.com"}
    log.info("Using identity %s <%s>", profile.get("name"), profile.get("email"))

    if dry_run or not shutil.which("npm"):
        log.info("[dry-run] would publish %s to %s", name, registry)
        return

    with temporary_directory("npm") as tmp:
        (tmp / "package.json").write_text(payload)
        proc = await asyncio.create_subprocess_exec(
            "npm",
            "publish",
            "--registry",
            registry,
            cwd=str(tmp),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await proc.communicate()
        if proc.returncode == 0:
            log.info("Published %s", name)
        else:
            log.error("npm publish failed: %s", err.decode().strip())
