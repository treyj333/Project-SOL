"""Abstract base classes for SOL voice backends."""

from abc import ABC, abstractmethod


class VoiceInput(ABC):
    """Base class for speech-to-text input."""

    @abstractmethod
    def listen(self) -> str:
        """Listen for speech and return recognized text."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this STT backend is ready."""
        ...


class VoiceOutput(ABC):
    """Base class for text-to-speech output."""

    @abstractmethod
    def speak(self, text: str) -> None:
        """Speak the given text aloud."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this TTS backend is ready."""
        ...
