"""Plugin API for DeathConfuser."""
from __future__ import annotations

from typing import List, Type


class Plugin:
    """Base plugin interface."""
    name = "base"

    async def scan(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError

    async def publish(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError


def load_plugins(classes: List[Type[Plugin]]) -> List[Plugin]:
    """Instantiate plugin classes."""
    return [cls() for cls in classes]


__all__ = ["Plugin", "load_plugins"]
