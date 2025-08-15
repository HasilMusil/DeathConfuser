"""Build exploitation chains from discovered vulnerabilities."""
from __future__ import annotations

from typing import Dict, List


class ChainBuilder:
    """Construct exploitation chains based on vulnerability details."""

    async def build(self, vuln: Dict[str, str]) -> List[str]:
        """Return a sequence of exploitation steps."""
        target = vuln.get("target", "unknown")
        package = vuln.get("package", vuln.get("vuln", "pkg"))
        return [
            f"leverage {package} on {target}",
            "pivot to CI/CD",
            "achieve RCE",
        ]


__all__ = ["ChainBuilder"]
