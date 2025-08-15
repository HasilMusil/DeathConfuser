"""Publish NuGet packages (simulated)."""
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


async def publish(name: str, payload: str, source: str = "https://api.nuget.org/v3/index.json", dry_run: bool = True) -> None:
    """Publish a NuGet package using ``dotnet`` if unclaimed."""

    scanner = Scanner()
    if not await scanner.is_unclaimed(name):
        log.info("Package %s already exists", name)
        return

    infra = InfraManager()
    profile = await infra.generate_burner_identity()
    log.info("Using identity %s <%s>", profile.get("name"), profile.get("email"))
    log.debug("UA %s version %s", profile.get("user_agent"), profile.get("version"))
    await asyncio.sleep(profile.get("delay", 0))

    if dry_run or not shutil.which("dotnet"):
        log.info("[dry-run] would push %s", name)
        return

    with temporary_directory("nuget") as tmp:
        proj = tmp / f"{name}.csproj"
        proj.write_text(payload)
        proc = await asyncio.create_subprocess_exec(
            "dotnet",
            "pack",
            proj,
            cwd=str(tmp),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        nupkg = next(tmp.glob("*.nupkg"), None)
        if nupkg:
            proc2 = await asyncio.create_subprocess_exec(
                "dotnet",
                "nuget",
                "push",
                str(nupkg),
                "--source",
                source,
                cwd=str(tmp),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, err = await proc2.communicate()
            if proc2.returncode == 0:
                log.info("Pushed %s", name)
            else:
                log.error("nuget push failed: %s", err.decode().strip())


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
