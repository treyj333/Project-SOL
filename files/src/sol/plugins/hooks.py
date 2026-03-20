"""Plugin hook execution utilities."""

from typing import List, Optional
from sol.plugins.base_plugin import BasePlugin


def run_on_user_input(plugins: List[BasePlugin], text: str) -> Optional[str]:
    """Run on_user_input hook on all plugins.

    Returns the first non-None response (plugin override),
    or None if no plugin wants to handle it.
    """
    for plugin in plugins:
        try:
            result = plugin.on_user_input(text)
            if result is not None:
                return result
        except Exception:
            pass
    return None


def run_on_response(plugins: List[BasePlugin], user_input: str, response: str) -> str:
    """Run on_response hook on all plugins, chaining the response."""
    for plugin in plugins:
        try:
            response = plugin.on_response(user_input, response)
        except Exception:
            pass
    return response


def run_on_session_start(plugins: List[BasePlugin]) -> None:
    """Run on_session_start hook on all plugins."""
    for plugin in plugins:
        try:
            plugin.on_session_start()
        except Exception:
            pass


def run_on_session_end(plugins: List[BasePlugin]) -> None:
    """Run on_session_end hook on all plugins."""
    for plugin in plugins:
        try:
            plugin.on_session_end()
        except Exception:
            pass


def get_all_commands(plugins: List[BasePlugin]) -> dict:
    """Collect all slash commands from all plugins."""
    commands = {}
    for plugin in plugins:
        try:
            cmds = plugin.get_commands()
            commands.update(cmds)
        except Exception:
            pass
    return commands
