"""JavaScript parsing utilities.

This module provides lightweight helpers for scanning JavaScript sources and
HTML documents for package references. It intentionally avoids implementing a
full JavaScript parser for performance reasons, instead relying on a set of
regular expressions that cover common cases such as ``import`` and ``require``
statements. The helpers are used during recon to discover internal package
names that might be referenced within front‑end code or bundled assets.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Set

__all__ = [
    "extract_packages",
    "extract_from_file",
    "extract_from_html",
    "extract_from_sources",
    "extract_from_bundle",
]

# Regex matches import and require statements. It is intentionally simple and
# not a full JavaScript parser, but works well for common patterns.
PACKAGE_RE = re.compile(
    r"(?:import\s+(?:.*?\s+from\s*)?|require\(|import\(|define\(\s*\[?)\s*['\"]([^'\"]+)['\"]",
    re.IGNORECASE,
)

# Webpack style bundle references look like {"path/to/module":function(...)}
BUNDLE_RE = re.compile(r'"([^\"]+)":\s*function\s*\(', re.IGNORECASE)

# Simple regex to pull contents of <script> tags for HTML scanning
SCRIPT_RE = re.compile(
    r"<script[^>]*>(.*?)</script>", re.IGNORECASE | re.DOTALL
)


def _normalize(pkg: str) -> str:
    """Normalize a module path by removing common noise like relative prefixes."""

    pkg = pkg.split("?")[0]
    pkg = pkg.lstrip("./")
    while pkg.startswith("../"):
        pkg = pkg[3:]
    return pkg


def extract_packages(code: str) -> Set[str]:
    """Return a set of packages referenced in a block of JavaScript."""

    matches = set(PACKAGE_RE.findall(code)) | set(BUNDLE_RE.findall(code))
    return {_normalize(m) for m in matches if m}


def extract_from_file(path: str | Path) -> Set[str]:
    """Read a JavaScript file from disk and return referenced packages."""

    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    return extract_packages(text)


def extract_from_bundle(path: str | Path) -> Set[str]:
    """Parse a bundled JavaScript file (like Webpack output)."""

    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    return extract_packages(text)


def extract_from_html(html: str) -> Set[str]:
    """Scan inline <script> blocks in HTML for package references."""

    packages: Set[str] = set()
    for script in SCRIPT_RE.findall(html):
        packages.update(extract_packages(script))
    return packages


def extract_from_sources(sources: Iterable[str | Path]) -> Set[str]:
    """Convenience wrapper to process multiple files or HTML blobs."""

    results: Set[str] = set()
    for src in sources:
        if isinstance(src, Path) or Path(str(src)).exists():
            results.update(extract_from_file(Path(src)))
        else:
            results.update(extract_packages(str(src)))
    return results

