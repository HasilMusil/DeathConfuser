"""Monitor registries for newly available package names."""
from __future__ import annotations

import asyncio
from typing import Iterable, Callable, Awaitable, Protocol, List


class RegistryClient(Protocol):
    async def is_unclaimed(self, name: str) -> bool: ...
    async def claim(self, name: str) -> None: ...


class RegistryMonitor:
    """Class-based registry watcher that can claim unclaimed packages."""
    def __init__(self, scanner: RegistryClient) -> None:
        self.scanner = scanner

    async def watch(self, packages: Iterable[str], claim: Callable[[str], Awaitable[None]]) -> None:
        for name in packages:
            if await self.scanner.is_unclaimed(name):
                await claim(name)
            await asyncio.sleep(0)


async def monitor(registry: RegistryClient, names: Iterable[str]) -> List[str]:
    """Functional helper for simple registry monitoring."""
    claimed: List[str] = []
    for name in names:
        if await registry.is_unclaimed(name):
            await registry.claim(name)
            claimed.append(name)
    return claimed


__all__ = ["RegistryMonitor", "monitor", "RegistryClient"]
