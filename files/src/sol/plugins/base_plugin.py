"""Base plugin class for SOL extensions."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Callable


class PluginContext:
    """Context object given to plugins — provides access to SOL's systems."""

    def __init__(self, memory, config: dict, speak: Callable, display: Callable):
        self.memory = memory
        self.config = config
        self.speak = speak
        self.display = display

    def get_friend_name(self) -> Optional[str]:
        return self.memory.get_friend_name()


class BasePlugin(ABC):
    """Base class for SOL plugins.

    To create a plugin:
    1. Create a directory in plugins/ with a plugin.py file
    2. Define a class extending BasePlugin
    3. Implement at minimum: name property and on_load method
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin name."""
        ...

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return ""

    def on_load(self, ctx: PluginContext) -> None:
        """Called when the plugin is loaded."""
        self.ctx = ctx

    def on_unload(self) -> None:
        """Called when the plugin is unloaded."""
        pass

    def on_user_input(self, text: str) -> Optional[str]:
        """Called before the brain processes input.

        Return a string to override the brain's response.
        Return None to let the brain handle it.
        """
        return None

    def on_response(self, user_input: str, response: str) -> str:
        """Called after the brain generates a response.

        Can modify the response. Must return a string.
        """
        return response

    def on_session_start(self) -> None:
        """Called when a conversation session begins."""
        pass

    def on_session_end(self) -> None:
        """Called when a conversation session ends."""
        pass

    def get_commands(self) -> Dict[str, Callable]:
        """Return slash-commands this plugin handles.

        Example: {"/weather": self.handle_weather}
        """
        return {}
