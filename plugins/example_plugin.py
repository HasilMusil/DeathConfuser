"""Example plugin implementation."""
from __future__ import annotations

from .plugin_api import Plugin


class ExamplePlugin(Plugin):
    name = "example"

    async def scan(self, *args, **kwargs):
        """Dummy scan method."""
        return ["pkg1"]

    async def publish(self, *args, **kwargs):
        """Dummy publish method."""
        return True


__all__ = ["ExamplePlugin"]
