"""RubyGems publication utilities."""
from __future__ import annotations

import asyncio
import random
import shutil
from typing import Optional

from core.logger import get_logger
from modules.rubygems.scanner import Scanner
from opsec import load_profiles
from utils.fs_utils import temporary_directory

log = get_logger(__name__)


async def publish(name: str, payload: str, host: str = "https://rubygems.org", dry_run: bool = True) -> None:
    """Publish ``payload`` gem if ``name`` is unclaimed."""

    scanner = Scanner(["https://rubygems.org/api/v1/gems/{name}.json"])
    if not await scanner.is_unclaimed(name):
        log.info("Gem %s already exists", name)
        return

    profiles = load_profiles()
    profile = random.choice(profiles) if profiles else {"name": "tester", "email": "test@example.com"}
    log.info("Using identity %s <%s>", profile.get("name"), profile.get("email"))

    if dry_run or not shutil.which("gem"):
        log.info("[dry-run] would push %s to %s", name, host)
        return

    with temporary_directory("gem") as tmp:
        (tmp / f"{name}.gemspec").write_text(payload)
        proc = await asyncio.create_subprocess_exec(
            "gem",
            "build",
            f"{name}.gemspec",
            cwd=str(tmp),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        proc2 = await asyncio.create_subprocess_exec(
            "gem",
            "push",
            f"{name}-0.0.1.gem",
            "--host",
            host,
            cwd=str(tmp),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, err = await proc2.communicate()
        if proc2.returncode == 0:
            log.info("Pushed gem %s", name)
        else:
            log.error("gem push failed: %s", err.decode().strip())
