"""Monitor registries for newly available package names."""
from __future__ import annotations

import asyncio
from typing import Iterable, Callable, Awaitable


class RegistryMonitor:
    def __init__(self, scanner) -> None:
        self.scanner = scanner

    async def watch(self, packages: Iterable[str], claim: Callable[[str], Awaitable[None]]) -> None:
        for name in packages:
            if await self.scanner.is_unclaimed(name):
                await claim(name)
            await asyncio.sleep(0)


__all__ = ["RegistryMonitor"]
