"""Abstract base class for SOL brain backends."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseBrain(ABC):
    """Base class for SOL's thinking engine."""

    @abstractmethod
    def think(self, user_input: str) -> str:
        """Process user input and generate a response."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this brain backend is ready to use."""
        ...

    @abstractmethod
    def get_context(self) -> List[Dict[str, Any]]:
        """Return the current conversation context."""
        ...
