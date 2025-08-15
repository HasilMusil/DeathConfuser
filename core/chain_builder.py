"""Auto build simple exploit chains."""
from __future__ import annotations

from typing import Dict, List


class ChainBuilder:
    def build(self, info: Dict[str, str]) -> List[str]:
        vuln = info.get("vuln", "vulnerability")
        return [
            f"identify {vuln}",
            "abuse CI/CD",
            "demonstrate RCE",
        ]


__all__ = ["ChainBuilder"]
