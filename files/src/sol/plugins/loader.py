"""Plugin discovery and loading."""

import os
import importlib.util
import inspect
from typing import List

from sol.plugins.base_plugin import BasePlugin, PluginContext


def discover_plugins(plugin_dir: str, app) -> List[BasePlugin]:
    """Scan plugin directory for valid plugins and load them.

    A valid plugin is a subdirectory containing a plugin.py file
    with a class that extends BasePlugin.

    Args:
        plugin_dir: Path to the plugins directory.
        app: The SolApp instance (used to create PluginContext).

    Returns:
        List of loaded and initialized plugin instances.
    """
    plugins = []

    if not os.path.isdir(plugin_dir):
        return plugins

    for item in os.listdir(plugin_dir):
        item_path = os.path.join(plugin_dir, item)

        if not os.path.isdir(item_path):
            continue

        plugin_file = os.path.join(item_path, "plugin.py")
        if not os.path.isfile(plugin_file):
            continue

        try:
            plugin = _load_plugin(plugin_file, item, app)
            if plugin:
                plugins.append(plugin)
        except Exception:
            pass  # Skip broken plugins silently

    return plugins


def _load_plugin(plugin_file: str, plugin_name: str, app):
    """Load a single plugin from its plugin.py file."""
    spec = importlib.util.spec_from_file_location(f"sol_plugin_{plugin_name}", plugin_file)
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find the class extending BasePlugin
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, BasePlugin) and obj is not BasePlugin:
            instance = obj()
            ctx = PluginContext(
                memory=app.memory,
                config=app.config,
                speak=app.speak,
                display=app.ui.display_message,
            )
            instance.on_load(ctx)
            return instance

    return None
