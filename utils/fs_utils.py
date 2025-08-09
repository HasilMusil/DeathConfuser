"""Filesystem helpers for sandbox-aware operations."""

from __future__ import annotations

import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

__all__ = ["atomic_write", "temporary_directory", "cleanup", "scan_workspace"]


@contextmanager
def temporary_directory(prefix: str = "dc") -> Iterator[Path]:
    """Yield a temporary directory and clean it up afterwards."""

    with tempfile.TemporaryDirectory(prefix=prefix) as tmp:
        path = Path(tmp)
        yield path


def atomic_write(path: str | Path, data: str) -> None:
    """Write data to a file atomically."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(target.parent)) as tf:
        tf.write(data)
        temp_name = tf.name
    Path(temp_name).replace(target)


def cleanup(path: str | Path) -> None:
    """Remove a file or directory if it exists."""

    p = Path(path)
    if p.is_dir():
        shutil.rmtree(p, ignore_errors=True)
    else:
        try:
            p.unlink()
        except FileNotFoundError:
            pass


@contextmanager
def scan_workspace(prefix: str = "dc", persist: bool = False) -> Iterator[Path]:
    """Yield a directory for a scan session and optionally remove on exit."""

    path = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        yield path
    finally:
        if not persist:
            shutil.rmtree(path, ignore_errors=True)

