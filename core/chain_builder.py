"""Build exploitation chains from discovered vulnerabilities."""
from __future__ import annotations

from typing import Dict, List


class ChainBuilder:
    """Construct exploitation chains based on vulnerability details."""

    def build(self, vuln: Dict[str, str]) -> List[str]:
        """Return a sequence of exploitation steps.

        Parameters
        ----------
        vuln:
            A dictionary describing the vulnerability. Expected keys include
            ``target`` and ``package``.
        """

        target = vuln.get("target", "unknown")
        package = vuln.get("package", vuln.get("vuln", "pkg"))
        return [
            f"leverage {package} on {target}",
            "pivot to CI/CD",
            "achieve RCE",
        ]


async def build_chain(vuln: Dict[str, str]) -> List[str]:
    """Async wrapper for :meth:`ChainBuilder.build`.

    This mirrors the interface expected by tests and higher level modules.
    """

    builder = ChainBuilder()
    return builder.build(vuln)


__all__ = ["ChainBuilder", "build_chain"]
