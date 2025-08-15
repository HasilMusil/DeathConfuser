"""Example plugin using the API."""
from __future__ import annotations

from .plugin_api import register


class ExamplePlugin:
    name = "example"

    async def run(self) -> None:
        return None


register(ExamplePlugin())
