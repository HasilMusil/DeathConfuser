"""Simple plugin API."""
from __future__ import annotations

from typing import Protocol


class Plugin(Protocol):
    name: str
    async def run(self) -> None: ...


PLUGINS: dict[str, Plugin] = {}


def register(plugin: Plugin) -> None:
    PLUGINS[plugin.name] = plugin
