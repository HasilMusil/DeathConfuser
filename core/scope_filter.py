"""Filter out-of-scope domains."""
from __future__ import annotations

from typing import Iterable, List


def filter_targets(targets: Iterable[str], oos_patterns: Iterable[str]) -> List[str]:
    patterns = [p.lower() for p in oos_patterns]
    result = []
    for t in targets:
        if any(p in t.lower() for p in patterns):
            continue
        result.append(t)
    return result
