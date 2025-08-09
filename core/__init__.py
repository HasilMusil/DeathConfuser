"""Core package initialization for DeathConfuser.

This module loads the global configuration and logger instances so that
other modules can simply import them. The intention is to minimise boilerplate
in the rest of the codebase.
"""

from __future__ import annotations

from typing import Optional

from .config import Config
from .logger import get_logger

__all__ = ["config", "logger", "init"]

config: Config
logger = get_logger("deathconfuser")


def init(config_path: Optional[str] = None, preset: Optional[str] = None) -> None:
    """Initialise global configuration and logger.

    This should be called by the CLI or any entry-point before performing
    operations. Subsequent calls simply update the global instances.
    """

    global config, logger
    config = Config.load(config_path, preset)
    logger = get_logger("deathconfuser", config.log_file, config.log_level)
    logger.debug("Configuration loaded")


# Initialise with defaults on import so that simple scripts can just import
# `core` and have reasonable defaults.
init()

