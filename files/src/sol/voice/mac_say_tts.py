"""macOS native TTS — uses the built-in 'say' command. Zero dependencies."""

import shutil
import subprocess
import sys

from sol.voice.base import VoiceOutput


class MacSayTTS(VoiceOutput):
    """Text-to-speech using macOS native 'say' command."""

    def __init__(self, voice: str = "Daniel", rate: int = 180):
        self.voice = voice
        self.rate = rate
        self._available = (
            sys.platform == "darwin"
            and shutil.which("say") is not None
        )

    def is_available(self) -> bool:
        return self._available

    def speak(self, text: str) -> None:
        """Speak text using macOS say command."""
        if not self._available or not text:
            return

        # Clean text for shell safety — say reads from args, not shell
        try:
            subprocess.run(
                ["say", "-v", self.voice, "-r", str(self.rate), text],
                check=False,
                timeout=30,
            )
        except (subprocess.TimeoutExpired, OSError):
            pass
