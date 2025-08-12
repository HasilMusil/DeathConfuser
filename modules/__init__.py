"""Utilities for loading package manager modules."""
from __future__ import annotations

import types
from dataclasses import dataclass
from importlib import import_module
from typing import Set

from ..core.logger import get_logger

__all__ = ["load_module", "MODULES", "typo_variants", "Scanner"]

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# Legacy scanner loading
# ---------------------------------------------------------------------------

BASE = __name__
SCANNER_MODULES = {
    "npm": f"{BASE}.npm",
    "pypi": f"{BASE}.pypi",
    "maven": f"{BASE}.maven",
    "nuget": f"{BASE}.nuget",
    "composer": f"{BASE}.composer",
    "rubygems": f"{BASE}.rubygems",
    "golang": f"{BASE}.golang",
    "rust": f"{BASE}.rust",
    "docker": f"{BASE}.docker",
    "terraform": f"{BASE}.terraform",
}


@dataclass
class ModuleLoader:
    """Container for scanner, payload and publisher classes."""

    Scanner: type
    payload: types.ModuleType
    publisher: types.ModuleType


def load_module(name: str) -> ModuleLoader:
    """Dynamically load a package manager module by name."""

    base = SCANNER_MODULES.get(name)
    if not base:
        raise ValueError(f"Unknown module: {name}")

    log.debug("Loading module %s", name)
    scanner_mod = import_module(f"{base}.scanner")
    payload_mod = import_module(f"{base}.payload")
    publisher_mod = import_module(f"{base}.publisher")
    return ModuleLoader(
        Scanner=getattr(scanner_mod, "Scanner"),
        payload=payload_mod,
        publisher=publisher_mod,
    )


def typo_variants(name: str) -> Set[str]:
    """Generate basic typosquat variants for a package name."""

    variants: Set[str] = set()
    if len(name) < 3:
        return variants

    # missing character
    for i in range(len(name)):
        variants.add(name[:i] + name[i + 1 :])

    # transposition
    for i in range(len(name) - 1):
        variants.add(name[:i] + name[i + 1] + name[i] + name[i + 2 :])

    # double character
    for i in range(len(name)):
        variants.add(name[:i] + name[i] + name[i] + name[i + 1 :])

    return {v for v in variants if v and v != name}


from .terraform.scanner import Scanner  # noqa: E402

# ---------------------------------------------------------------------------
# Registry search modules
# ---------------------------------------------------------------------------

from . import (
    npm_registry as npm,
    pypi_registry as pypi,
    maven_registry as maven,
    nuget_registry as nuget,
    composer_registry as composer,
    rubygems_registry as rubygems,
    golang_registry as golang,
    rust_registry as rust,
    cpan,
    hackage,
    hexpm,
    swiftpm,
    cocoapods,
    conda,
    meteor,
)

MODULES = {
    "npm": npm,
    "pypi": pypi,
    "maven": maven,
    "nuget": nuget,
    "composer": composer,
    "rubygems": rubygems,
    "golang": golang,
    "rust": rust,
    "cpan": cpan,
    "hackage": hackage,
    "hexpm": hexpm,
    "swiftpm": swiftpm,
    "cocoapods": cocoapods,
    "conda": conda,
    "meteor": meteor,
}
