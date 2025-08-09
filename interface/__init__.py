"""Public interfaces for DeathConfuser."""

from .cli import main as cli_main
from .webui import run_webui
from .api import run_api

__all__ = ["cli_main", "run_webui", "run_api"]
