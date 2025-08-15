"""Simple target scope filtering."""
from __future__ import annotations

from typing import Iterable


class ScopeFilter:
    def __init__(self, allowed: Iterable[str]) -> None:
        self.allowed = list(allowed)

    def in_scope(self, url: str) -> bool:
        return any(part in url for part in self.allowed)


__all__ = ["ScopeFilter"]
