"""Publish Composer packages (simulated)."""
from __future__ import annotations

import asyncio
import random
import shutil

from ...core.logger import get_logger
from .scanner import Scanner
from ...opsec import load_profiles
from ...utils.fs_utils import temporary_directory

log = get_logger(__name__)


async def publish(name: str, payload: str, repository: str = "https://packagist.org", dry_run: bool = True) -> None:
    """Publish a Composer package using ``composer`` if unclaimed."""

    scanner = Scanner()
    if not await scanner.is_unclaimed(name):
        log.info("Package %s already exists", name)
        return

    profile = random.choice(load_profiles()) if load_profiles() else {"name": "test", "email": "test@example.com"}
    log.info("Using identity %s <%s>", profile.get("name"), profile.get("email"))

    if dry_run or not shutil.which("composer"):
        log.info("[dry-run] would submit %s", name)
        return

    with temporary_directory("composer") as tmp:
        (tmp / "composer.json").write_text(payload)
        proc = await asyncio.create_subprocess_exec(
            "composer",
            "publish",
            cwd=str(tmp),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, err = await proc.communicate()
        if proc.returncode == 0:
            log.info("Submitted %s", name)
        else:
            log.error("composer publish failed: %s", err.decode().strip())
