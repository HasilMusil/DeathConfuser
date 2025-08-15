"""Monitor registries for new unclaimed packages."""
from __future__ import annotations

from typing import Iterable, List, Protocol


class RegistryClient(Protocol):
    async def is_unclaimed(self, name: str) -> bool: ...
    async def claim(self, name: str) -> None: ...


async def monitor(registry: RegistryClient, names: Iterable[str]) -> List[str]:
    claimed: List[str] = []
    for name in names:
        if await registry.is_unclaimed(name):
            await registry.claim(name)
            claimed.append(name)
    return claimed
