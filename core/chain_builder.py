"""Build exploitation chains from discovered vulnerabilities."""
from __future__ import annotations

from typing import Dict, List


async def build_chain(vuln: Dict[str, str]) -> List[str]:
    """Return a sequence of exploitation steps."""
    target = vuln.get("target", "unknown")
    return [f"leverage {vuln.get('package', 'pkg')} on {target}", "pivot to ci/cd", "achieve rce"]
