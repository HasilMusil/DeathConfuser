"""Rust crate publisher."""
from __future__ import annotations

import asyncio
import random
import shutil

from ...core.logger import get_logger
from .scanner import Scanner
from ...opsec import load_profiles
from ...utils.fs_utils import temporary_directory

log = get_logger(__name__)


async def publish(name: str, payload: str, registry: str = "https://crates.io", dry_run: bool = True) -> None:
    """Publish crate payload if unclaimed."""

    scanner = Scanner()
    if not await scanner.is_unclaimed(name):
        log.info("Crate %s already exists", name)
        return

    profiles = load_profiles()
    profile = random.choice(profiles) if profiles else {"name": "tester", "email": "test@example.com"}
    log.info("Using identity %s <%s>", profile.get("name"), profile.get("email"))

    if dry_run or not shutil.which("cargo"):
        log.info("[dry-run] would publish %s to %s", name, registry)
        return

    with temporary_directory("cargo") as tmp:
        (tmp / "Cargo.toml").write_text(payload)
        proc = await asyncio.create_subprocess_exec(
            "cargo",
            "package",
            cwd=str(tmp),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        proc2 = await asyncio.create_subprocess_exec(
            "cargo",
            "publish",
            "--registry",
            registry,
            cwd=str(tmp),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, err = await proc2.communicate()
        if proc2.returncode == 0:
            log.info("Published crate %s", name)
        else:
            log.error("cargo publish failed: %s", err.decode().strip())
