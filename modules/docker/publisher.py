"""Docker image publisher."""
from __future__ import annotations

import asyncio
import random
import shutil

from core.logger import get_logger
from modules.docker.scanner import Scanner
from opsec import load_profiles
from utils.fs_utils import temporary_directory

log = get_logger(__name__)


async def publish(name: str, payload: str, registry: str = "docker.io", dry_run: bool = True) -> None:
    """Publish Dockerfile ``payload`` if repository is unclaimed."""

    scanner = Scanner()
    if not await scanner.is_unclaimed(name):
        log.info("Docker repo %s already exists", name)
        return

    profiles = load_profiles()
    profile = random.choice(profiles) if profiles else {"name": "tester", "email": "test@example.com"}
    log.info("Using identity %s <%s>", profile.get("name"), profile.get("email"))

    if dry_run or not shutil.which("docker"):
        log.info("[dry-run] would push %s to %s", name, registry)
        return

    with temporary_directory("docker") as tmp:
        (tmp / "Dockerfile").write_text(payload)
        proc = await asyncio.create_subprocess_exec(
            "docker",
            "build",
            "-t",
            f"{registry}/{name}:latest",
            str(tmp),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        proc2 = await asyncio.create_subprocess_exec(
            "docker",
            "push",
            f"{registry}/{name}:latest",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, err = await proc2.communicate()
        if proc2.returncode == 0:
            log.info("Pushed docker image %s", name)
        else:
            log.error("docker push failed: %s", err.decode().strip())
