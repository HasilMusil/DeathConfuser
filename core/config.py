"""Configuration loader and argument parser."""
from __future__ import annotations

import argparse
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_CONFIG_PATH = Path('config.yaml')
PRESET_DIR = Path('presets')


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open('r') as f:
        return yaml.safe_load(f) or {}


def _set_deep(mapping: Dict[str, Any], dotted_key: str, value: Any) -> None:
    """Set ``mapping[a][b] = value`` for dot-separated keys."""
    parts = dotted_key.split(".")
    target = mapping
    for part in parts[:-1]:
        if part not in target or not isinstance(target[part], dict):
            target[part] = {}
        target = target[part]
    target[parts[-1]] = value


@dataclass
class Config:
    data: Dict[str, Any] = field(default_factory=dict)

    @property
    def log_file(self) -> Optional[str]:
        return self.data.get('log_file')

    @property
    def log_level(self) -> str:
        return self.data.get('log_level', 'INFO')

    @classmethod
    def load(cls, config_path: Optional[str] = None, preset: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None) -> 'Config':
        """Load configuration from defaults, preset and custom file."""
        config = _load_yaml(DEFAULT_CONFIG_PATH)

        if preset:
            preset_path = PRESET_DIR / preset
            if not preset_path.suffix:
                preset_path = preset_path.with_suffix('.yaml')
            config.update(_load_yaml(preset_path))
        else:
            preset_name = config.get('default_preset')
            if preset_name:
                config.update(_load_yaml(PRESET_DIR / f'{preset_name}.yaml'))

        if config_path:
            config.update(_load_yaml(Path(config_path)))

        if overrides:
            for key, value in overrides.items():
                _set_deep(config, key, value)

        return cls(config)


class ArgumentParser(argparse.ArgumentParser):
    """Argument parser used across the project."""

    def __init__(self) -> None:
        super().__init__(description="DeathConfuser framework")
        self.add_argument("-c", "--config", help="Path to config file")
        self.add_argument("-p", "--preset", help="Preset profile name")
        self.add_argument(
            "--set",
            action="append",
            metavar="KEY=VAL",
            help="Override arbitrary config values",
        )

    def parse(self, argv: Optional[list[str]] = None) -> Config:
        args = self.parse_args(argv)

        overrides: Dict[str, Any] = {}
        if args.set:
            for item in args.set:
                if "=" not in item:
                    continue
                key, val = item.split("=", 1)
                overrides[key.strip()] = val.strip()

        return Config.load(args.config, args.preset, overrides)
