"""Minimal plugin API."""
from __future__ import annotations

from typing import List, Type


class Plugin:
    name = "base"

    async def scan(self, *args, **kwargs):  # pragma: no cover - interface
        raise NotImplementedError

    async def publish(self, *args, **kwargs):  # pragma: no cover - interface
        raise NotImplementedError


def load_plugins(classes: List[Type[Plugin]]) -> List[Plugin]:
    return [cls() for cls in classes]


__all__ = ["Plugin", "load_plugins"]
