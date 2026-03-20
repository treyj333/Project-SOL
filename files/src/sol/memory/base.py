"""Abstract base class for SOL memory backends."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class MemoryStore(ABC):
    """Base class for SOL's memory system."""

    @abstractmethod
    def get_friend_name(self) -> Optional[str]:
        ...

    @abstractmethod
    def set_friend_name(self, name: str) -> None:
        ...

    @abstractmethod
    def get_facts(self, limit: int = 10, category: Optional[str] = None) -> List[str]:
        ...

    @abstractmethod
    def add_fact(self, fact: str, category: str = "general") -> None:
        ...

    @abstractmethod
    def get_preferences(self, limit: int = 10) -> List[Dict[str, str]]:
        ...

    @abstractmethod
    def add_preference(self, item: str, sentiment: str = "like") -> None:
        ...

    @abstractmethod
    def get_mood_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def add_mood(self, mood: str, intensity: float = 0.5, trigger: Optional[str] = None) -> None:
        ...

    @abstractmethod
    def get_topics(self, limit: int = 10) -> List[str]:
        ...

    @abstractmethod
    def add_topic(self, topic: str) -> None:
        ...

    @abstractmethod
    def get_conversations_count(self) -> int:
        ...

    @abstractmethod
    def increment_conversations(self) -> int:
        ...

    @abstractmethod
    def get_first_met(self) -> Optional[str]:
        ...

    @abstractmethod
    def set_first_met(self, timestamp: str) -> None:
        ...

    @abstractmethod
    def get_last_talked(self) -> Optional[str]:
        ...

    @abstractmethod
    def set_last_talked(self, timestamp: str) -> None:
        ...

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Return all metadata as a dict for display purposes."""
        ...

    def supports_feature(self, feature: str) -> bool:
        """Check if this memory backend supports a given feature."""
        return False
