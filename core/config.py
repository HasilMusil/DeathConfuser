"""Advanced configuration loader with validation and overrides.

This module implements a small schema driven configuration system used by
DeathConfuser.  The configuration is composed of several sections which are
merged from a number of sources in the following order (lowest to highest
precedence):

1. The project default ``config.yaml``.
2. A preset file from ``presets/<name>.yaml`` – either explicitly provided or
   referenced via ``global.default_preset``.
3. An optional external configuration file provided via ``-c``/``--config``.
4. Command line overrides supplied via ``--set`` using dotted keys.  List items
   can be targeted using ``index`` notation (``section.list[0]=foo``).

Each configuration field defines a default value, a type and optional
validation (e.g. choice restrictions).  Unknown fields or values of the wrong
type will raise ``ValueError`` during loading.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import yaml

DEFAULT_CONFIG_PATH = Path("config.yaml")
PRESET_DIR = Path("presets")


# ---------------------------------------------------------------------------
# Schema definition
# ---------------------------------------------------------------------------

Field = Dict[str, Any]


def _bool(val: str) -> bool:
    val = val.lower()
    if val in {"1", "true", "yes", "on"}:
        return True
    if val in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {val}")


SCHEMA: Dict[str, Field] = {
    "global": {
        "type": dict,
        "default": {},
        "schema": {
            "log_level": {
                "type": str,
                "default": "INFO",
                "choices": ["DEBUG", "INFO", "WARNING", "ERROR"],
            },
            "log_file": {"type": str, "default": "deathconfuser.log"},
            "default_preset": {"type": (str, type(None)), "default": None},
        },
    },
    "recon": {
        "type": dict,
        "default": {},
        "schema": {
            "wordlist": {"type": str, "default": "wordlists/common.txt"},
            "threads": {"type": int, "default": 10},
            "timeout": {"type": int, "default": 30},
            "user_agents": {
                "type": list,
                "default": ["Mozilla/5.0"],
                "subtype": str,
            },
            "mode": {
                "type": str,
                "default": "stealth",
                "choices": ["stealth", "aggressive", "passive"],
            },
            "v2_engine": {"type": bool, "default": False},
        },
    },
    "exploit": {
        "type": dict,
        "default": {},
        "schema": {
            "package_managers": {
                "type": list,
                "default": ["npm", "pip"],
                "subtype": str,
            },
            "auto_publish": {"type": bool, "default": False},
            "verify_callback": {"type": bool, "default": True},
            "callback": {
                "type": dict,
                "schema": {
                    "http_url": {"type": str, "default": ""},
                    "dns_domain": {"type": str, "default": ""},
                },
                "default": {},
            },
            "retries": {"type": int, "default": 3},
            "timeout": {"type": int, "default": 30},
        },
    },
    "payloads": {
        "type": dict,
        "default": {},
        "schema": {
            "polymorphic": {"type": bool, "default": False},
            "builder": {"type": str, "default": "template"},
            "stealth_sleep": {"type": int, "default": 0},
            "obfuscation": {
                "type": dict,
                "schema": {
                    "base64": {"type": bool, "default": False},
                    "xor": {"type": bool, "default": False},
                    "timing": {"type": bool, "default": False},
                },
                "default": {},
            },
        },
    },
    "opsec": {
        "type": dict,
        "default": {},
        "schema": {
            "proxy_rotation": {"type": bool, "default": False},
            "proxy_list": {"type": list, "default": [], "subtype": str},
            "use_tor": {"type": bool, "default": False},
            "doh_resolver": {"type": str, "default": ""},
            "sandbox_detect": {"type": bool, "default": False},
            "scrub_logs": {"type": bool, "default": False},
            "burner_profiles": {"type": bool, "default": False},
        },
    },
    "report": {
        "type": dict,
        "default": {},
        "schema": {
            "formats": {"type": list, "default": ["json"], "subtype": str},
            "output_dir": {"type": str, "default": "reports"},
            "template_dir": {"type": str, "default": "templates"},
            "callback_log": {"type": bool, "default": False},
        },
    },
    "concurrency": {
        "type": dict,
        "default": {},
        "schema": {
            "limit": {"type": int, "default": 10},
            "retries": {"type": int, "default": 1},
            "timeout": {"type": int, "default": 30},
        },
    },
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _deep_merge(base: Dict[str, Any], other: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge ``other`` into ``base`` and return ``base``."""

    for key, val in other.items():
        if (
            key in base
            and isinstance(base[key], dict)
            and isinstance(val, dict)
        ):
            _deep_merge(base[key], val)
        else:
            base[key] = val
    return base


_TOKEN_RE = re.compile(r"([^\.\[]+)(?:\[(\d+)\])?")


def _traverse_schema(key: str) -> Tuple[Field, Optional[Field]]:
    """Return schema field and parent for ``key``."""

    parts = _TOKEN_RE.findall(key)
    current: Field = SCHEMA
    field: Optional[Field] = None
    for name, _idx in parts:
        if name not in current:
            raise ValueError(f"Unknown configuration field: {key}")
        field = current[name]
        if field.get("type") is dict:
            current = field.get("schema", {})
        elif field.get("type") is list:
            # For list types, dive into element schema if provided
            subtype = field.get("subtype")
            if subtype is dict:
                current = field.get("schema", {})
            else:
                current = {}
        else:
            current = {}
    if field is None:
        raise ValueError(f"Unknown configuration field: {key}")
    return field, current if current is not SCHEMA else None


def _cast(value: str, field: Field) -> Any:
    """Cast string ``value`` according to ``field`` definition."""

    expected = field.get("type")
    if expected is bool:
        return _bool(value) if isinstance(value, str) else bool(value)
    if expected is int:
        return int(value)
    if expected is float:
        return float(value)
    if expected is list:
        if isinstance(value, str):
            # allow comma separated or YAML list
            if value.strip().startswith("["):
                parsed = yaml.safe_load(value)
            else:
                parsed = [v.strip() for v in value.split(",") if v.strip()]
        else:
            parsed = list(value)
        subtype = field.get("subtype")
        if subtype:
            return [_cast(v, {"type": subtype}) for v in parsed]
        return parsed
    if expected is dict:
        if isinstance(value, str):
            parsed = yaml.safe_load(value) or {}
        else:
            parsed = dict(value)
        schema = field.get("schema")
        if schema:
            return _apply_schema(schema, parsed, path="")
        return parsed
    if expected in (str, (str, type(None))):
        return str(value)
    return value


def _set_override(data: Dict[str, Any], key: str, raw_value: str) -> None:
    """Apply a single override ``key=value`` to ``data`` respecting schema."""

    tokens = _TOKEN_RE.findall(key)
    target = data
    schema_field: Field = SCHEMA
    for name, idx in tokens[:-1]:
        field = schema_field[name]
        if field.get("type") is list:
            # ensure list exists
            lst = target.setdefault(name, [])
            list_index = int(idx) if idx else 0
            while len(lst) <= list_index:
                lst.append({} if field.get("subtype") is dict else None)
            target = lst[list_index]
            if field.get("subtype") is dict:
                schema_field = field.get("schema", {})
            else:
                schema_field = {"type": field.get("subtype")}
        else:
            target = target.setdefault(name, {})
            schema_field = field.get("schema", {})

    last_name, last_idx = tokens[-1]
    field = schema_field[last_name]
    cast_val = _cast(raw_value, field)
    if last_idx:
        lst = target.setdefault(last_name, [])
        index = int(last_idx)
        while len(lst) <= index:
            lst.append(None)
        lst[index] = cast_val
    else:
        target[last_name] = cast_val


def _apply_schema(schema: Dict[str, Field], data: Dict[str, Any], path: str) -> Dict[str, Any]:
    """Validate ``data`` against ``schema`` and fill defaults."""

    result: Dict[str, Any] = {}
    for key, field in schema.items():
        if key in data:
            value = data[key]
        else:
            value = field.get("default")
        expected = field.get("type")
        if expected is dict:
            if value is None:
                value = {}
            if not isinstance(value, dict):
                raise ValueError(f"{path+key} must be a dict")
            value = _apply_schema(field.get("schema", {}), value, path + key + ".")
        elif expected is list:
            if not isinstance(value, list):
                raise ValueError(f"{path+key} must be a list")
            subtype = field.get("subtype")
            if subtype:
                subtype_field = {"type": subtype}
                value = [_cast(v, subtype_field) for v in value]
        else:
            if value is None and expected is not type(None):
                value = field.get("default")
            if not isinstance(value, expected):
                raise ValueError(f"{path+key} must be of type {expected}")
            if "choices" in field and value not in field["choices"]:
                raise ValueError(f"{path+key} must be one of {field['choices']}")
        result[key] = value

    # check for unknown fields
    extra = set(data.keys()) - set(schema.keys())
    if extra:
        raise ValueError(f"Unknown configuration fields: {', '.join(path + e for e in extra)}")
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class Config:
    """Object wrapper around the configuration dictionary.

    Provides both attribute and mapping style access to values.
    """

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    # --- mapping protocol -------------------------------------------------
    def __getitem__(self, key: str) -> Any:
        val = self._data[key]
        if isinstance(val, dict):
            return Config(val)
        return val

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    # --- attribute access -------------------------------------------------
    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            val = self._data[name]
            if isinstance(val, dict):
                return Config(val)
            return val
        raise AttributeError(name)

    # convenience properties for common fields
    @property
    def log_level(self) -> str:
        return self._data.get("global", {}).get("log_level", "INFO")

    @property
    def log_file(self) -> Optional[str]:
        return self._data.get("global", {}).get("log_file")

    @property
    def data(self) -> Dict[str, Any]:  # backward compat
        return self._data

    # ------------------------------------------------------------------
    @classmethod
    def load(
        cls,
        config_path: Optional[str] = None,
        preset: Optional[str] = None,
        overrides: Optional[Dict[str, str]] = None,
    ) -> "Config":
        """Load and validate the configuration."""

        config: Dict[str, Any] = _load_yaml(DEFAULT_CONFIG_PATH)

        # determine preset
        preset_name = preset or config.get("global", {}).get("default_preset")
        if preset_name:
            preset_path = PRESET_DIR / f"{preset_name}.yaml"
            config = _deep_merge(config, _load_yaml(preset_path))

        if config_path:
            config = _deep_merge(config, _load_yaml(Path(config_path)))

        if overrides:
            for k, v in overrides.items():
                _set_override(config, k, v)

        validated = _apply_schema(SCHEMA, config, path="")

        # record preset path for later reference
        if preset_name:
            validated["preset"] = preset_name
        if config_path:
            validated["config_path"] = config_path
        return cls(validated)


class ArgumentParser(argparse.ArgumentParser):
    """Argument parser that returns a :class:`Config` instance."""

    def __init__(self) -> None:
        super().__init__(description="DeathConfuser framework")
        self.add_argument("-c", "--config", help="Path to config file")
        self.add_argument("--preset", help="Preset profile name")
        self.add_argument(
            "--set",
            action="append",
            metavar="KEY=VAL",
            help="Override arbitrary config values",
        )

    def parse(self, argv: Optional[List[str]] = None) -> Config:
        args = self.parse_args(argv)
        overrides: Dict[str, str] = {}
        if args.set:
            for item in args.set:
                if "=" not in item:
                    raise SystemExit("--set expects KEY=VALUE")
                key, val = item.split("=", 1)
                overrides[key.strip()] = val.strip()
        return Config.load(args.config, args.preset, overrides)

