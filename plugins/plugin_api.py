"""Plugin API for DeathConfuser.

This module exposes a simple plugin registration system. Plugins are
implemented by subclassing :class:`Plugin`.  Each subclass with a ``name``
attribute is automatically registered in the global :data:`PLUGINS`
dictionary so they can be discovered without manual bookkeeping.
"""
from __future__ import annotations

from typing import Dict, List, Type


PLUGINS: Dict[str, Type["Plugin"]] = {}


class _PluginMeta(type):
    """Metaclass that registers plugin subclasses."""

    def __new__(mcls, name, bases, attrs):
        cls = super().__new__(mcls, name, bases, attrs)
        plugin_name = attrs.get("name")
        if plugin_name and plugin_name != "base":
            PLUGINS[plugin_name] = cls
        return cls


class Plugin(metaclass=_PluginMeta):
    """Base plugin interface."""

    name = "base"

    async def scan(self, *args, **kwargs):  # pragma: no cover
        """Scan for targets.

        Subclasses must implement this method.
        """

        raise NotImplementedError

    async def publish(self, *args, **kwargs):  # pragma: no cover
        """Publish results to an external system.

        Subclasses must implement this method.
        """

        raise NotImplementedError


def load_plugins(classes: List[Type[Plugin]]) -> List[Plugin]:
    """Instantiate plugin classes.

    Parameters
    ----------
    classes:
        A list of plugin classes to instantiate.
    """

    return [cls() for cls in classes]


__all__ = ["Plugin", "load_plugins", "PLUGINS"]
