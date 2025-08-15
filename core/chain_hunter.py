"""Locate related organization accounts for chaining."""
from __future__ import annotations

from typing import List


async def hunt(org: str) -> List[str]:
    return [f"{org}-dev", f"{org}-ci"]
