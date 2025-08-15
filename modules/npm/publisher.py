"""Simulate publishing NPM packages with optional real execution."""
from __future__ import annotations

import asyncio
import random
import shutil

from ...core.logger import get_logger
from ...core.concurrency import run_tasks
from .scanner import Scanner
from ...opsec.infra_manager import InfraManager
from ...utils.fs_utils import temporary_directory

log = get_logger(__name__)


async def publish(name: str, payload: str, registry: str = "https://registry.npmjs.org", dry_run: bool = True) -> None:
    """Publish ``payload`` if the package ``name`` is unclaimed."""

    scanner = Scanner([registry])
    if not await scanner.is_unclaimed(name):
        log.info("Package %s already exists", name)
        return

    infra = InfraManager()
    profile = await infra.generate_burner_identity()
    log.info("Using identity %s <%s>", profile.get("name"), profile.get("email"))
    log.debug("UA %s version %s", profile.get("user_agent"), profile.get("version"))
    await asyncio.sleep(profile.get("delay", 0))

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
