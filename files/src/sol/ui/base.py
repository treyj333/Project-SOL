"""Abstract base class for SOL UI backends."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class UIBase(ABC):
    """Base class for SOL's user interface."""

    @abstractmethod
    def display_message(self, text: str, style: str = "sol") -> None:
        """Display a message in the given style."""
        ...

    @abstractmethod
    def display_banner(self) -> None:
        """Display SOL's startup banner."""
        ...

    @abstractmethod
    def display_status(self, metadata: Dict[str, Any]) -> None:
        """Display SOL's memory status bar."""
        ...

    @abstractmethod
    def get_text_input(self, prompt: str = "") -> str:
        """Get text input from the user."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear the screen."""
        ...
