"""Very small in-memory registry used for tests and demos."""
from __future__ import annotations

class FakeRegistry:
    def __init__(self) -> None:
        self.claimed = set()

    async def is_unclaimed(self, name: str) -> bool:
        return name not in self.claimed

    async def claim(self, name: str) -> None:
        self.claimed.add(name)
