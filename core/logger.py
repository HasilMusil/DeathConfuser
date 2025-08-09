"""Logging utilities for DeathConfuser."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from colorama import Fore, Style, init as colorama_init

colorama_init()

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
COLOR_MAP = {
    'DEBUG': Fore.CYAN,
    'INFO': Fore.GREEN,
    'WARNING': Fore.YELLOW,
    'ERROR': Fore.RED,
    'CRITICAL': Fore.RED + Style.BRIGHT,
}


def _colorize(level: str, message: str) -> str:
    color = COLOR_MAP.get(level, '')
    return f"{color}{message}{Style.RESET_ALL}"


def get_logger(
    name: str,
    log_file: Optional[str] = None,
    level: str = 'INFO',
) -> logging.Logger:
    """Return a configured logger with console and optional file handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(
        logging.Formatter(LOG_FORMAT)
    )
    logger.addHandler(console_handler)

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(log_file, maxBytes=1048576, backupCount=3)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Wrap emit to colorize levelname for console
    old_emit = console_handler.emit

    def emit(record):
        record.msg = _colorize(record.levelname, record.msg)
        old_emit(record)

    console_handler.emit = emit  # type: ignore
    return logger


def get_target_logger(target: str, base_dir: str = "logs") -> logging.Logger:
    """Return a logger writing to a target-specific file."""
    safe = target.replace("/", "_").replace(":", "_")
    path = Path(base_dir) / f"{safe}.log"
    return get_logger(safe, str(path))
