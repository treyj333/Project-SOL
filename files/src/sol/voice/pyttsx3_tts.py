"""pyttsx3-based text-to-speech — uses OS native TTS."""

from sol.voice.base import VoiceOutput


class Pyttsx3TTS(VoiceOutput):
    """Text-to-speech using pyttsx3 (SAPI5/espeak/NSSpeechSynthesizer)."""

    def __init__(self, rate: int = 140, volume: float = 0.9):
        self.engine = None
        self._available = False

        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", rate)
            self.engine.setProperty("volume", volume)
            # Prefer a male voice for Rocky-like cadence
            voices = self.engine.getProperty("voices")
            if voices:
                for v in voices:
                    if "male" in v.name.lower() or "david" in v.name.lower():
                        self.engine.setProperty("voice", v.id)
                        break
            self._available = True
        except Exception:
            pass

    def is_available(self) -> bool:
        return self._available

    def speak(self, text: str) -> None:
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass
