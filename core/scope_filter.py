"""Target scope filtering utilities."""
from __future__ import annotations
from typing import Iterable, List


def filter_targets(targets: Iterable[str], oos_patterns: Iterable[str]) -> List[str]:
    """Functional filter that excludes targets matching any OOS pattern."""
    patterns = [p.lower() for p in oos_patterns]
    result = []
    for t in targets:
        if any(p in t.lower() for p in patterns):
            continue
        result.append(t)
    return result


class ScopeFilter:
    """Class-based scope filter."""
    def __init__(self, allowed: Iterable[str]) -> None:
        self.allowed = list(allowed)

    def in_scope(self, url: str) -> bool:
        return any(part in url for part in self.allowed)


__all__ = ["filter_targets", "ScopeFilter"]
