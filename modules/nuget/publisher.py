"""Publish NuGet packages (simulated)."""
from __future__ import annotations

import asyncio
import random
import shutil

from ...core.logger import get_logger
from .scanner import Scanner
from ...opsec import load_profiles
from ...utils.fs_utils import temporary_directory

log = get_logger(__name__)


async def publish(name: str, payload: str, source: str = "https://api.nuget.org/v3/index.json", dry_run: bool = True) -> None:
    """Publish a NuGet package using ``dotnet`` if unclaimed."""

    scanner = Scanner()
    if not await scanner.is_unclaimed(name):
        log.info("Package %s already exists", name)
        return

    profile = random.choice(load_profiles()) if load_profiles() else {"name": "test", "email": "test@example.com"}
    log.info("Using identity %s <%s>", profile.get("name"), profile.get("email"))

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
