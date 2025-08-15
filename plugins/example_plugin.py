"""Example plugin providing a dummy registry."""
from __future__ import annotations

from .plugin_api import Plugin


class ExamplePlugin(Plugin):
    name = "example"

    async def scan(self, *args, **kwargs):
        return ["pkg1"]

    async def publish(self, *args, **kwargs):
        return True
