"""RubyGems publication utilities."""
from __future__ import annotations

import asyncio
import random
import shutil
from typing import Optional

from ...core.logger import get_logger
from ...core.concurrency import run_tasks
from .scanner import Scanner
from ...opsec.infra_manager import InfraManager
from ...utils.fs_utils import temporary_directory

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
    log.debug("UA %s version %s", profile.get("user_agent"), profile.get("version"))
    await asyncio.sleep(profile.get("delay", 0))

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


async def publish_parallel(packages, limit=5, retries=3, **kwargs):
    async def _single(pkg):
        name, payload = pkg
        backoff = 1
        for _ in range(retries+1):
            try:
                await publish(name, payload, **kwargs)
                break
            except Exception:  # pragma: no cover - network errors
                await asyncio.sleep(backoff)
                backoff *= 2
    coros = [lambda p=p: _single(p) for p in packages]
    await run_tasks(coros, limit=limit)
