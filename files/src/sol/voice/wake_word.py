"""Wake word detection — "Hey Sol" ambient listening."""

import threading
import time
from typing import Optional

from sol.voice.base import VoiceInput


class WakeWordDetector:
    """Continuously listens for a wake phrase, then signals active mode."""

    def __init__(self, stt: VoiceInput, phrase: str = "hey sol"):
        self.stt = stt
        self.phrase = phrase.lower()
        self._active = False
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback = None

    def start(self, callback=None):
        """Start listening for the wake word in a background thread.

        Args:
            callback: Optional function to call when wake word is detected.
        """
        self._callback = callback
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the wake word listener."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def wait_for_wake(self) -> bool:
        """Block until wake word is detected. Returns True on detection."""
        while self._running:
            text = self.stt.listen()
            if text and self.phrase in text.lower():
                return True
            time.sleep(0.1)
        return False

    def _listen_loop(self):
        """Background thread that listens for the wake word."""
        while self._running:
            try:
                text = self.stt.listen()
                if text and self.phrase in text.lower():
                    self._active = True
                    if self._callback:
                        self._callback()
            except Exception:
                time.sleep(1)  # Avoid tight loop on error

    @property
    def is_active(self) -> bool:
        """Check if wake word was detected (resets after read)."""
        if self._active:
            self._active = False
            return True
        return False
