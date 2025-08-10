"""Terraform module publisher."""
from __future__ import annotations

import asyncio
import random
import shutil

from ...core.logger import get_logger
from .scanner import Scanner
from ...opsec import load_profiles
from ...utils.fs_utils import temporary_directory

log = get_logger(__name__)


async def publish(name: str, payload: str, registry: str = "terraform.io", dry_run: bool = True) -> None:
    """Publish Terraform module if unclaimed."""

    scanner = Scanner()
    if not await scanner.is_unclaimed(name):
        log.info("Module %s already exists", name)
        return

    profiles = load_profiles()
    profile = random.choice(profiles) if profiles else {"name": "tester", "email": "test@example.com"}
    log.info("Using identity %s <%s>", profile.get("name"), profile.get("email"))

    if dry_run or not shutil.which("git"):
        log.info("[dry-run] would publish %s to %s", name, registry)
        return

    with temporary_directory("tf") as tmp:
        (tmp / "main.tf").write_text(payload)
        await asyncio.create_subprocess_exec(
            "git",
            "init",
            cwd=str(tmp),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await asyncio.create_subprocess_exec(
            "git",
            "add",
            ".",
            cwd=str(tmp),
        )
        await asyncio.create_subprocess_exec(
            "git",
            "commit",
            "-m",
            "init",
            cwd=str(tmp),
        )
        log.info("Published Terraform module %s", name)
