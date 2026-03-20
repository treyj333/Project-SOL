"""Piper TTS — near-human quality offline text-to-speech."""

import io
import wave
from sol.voice.base import VoiceOutput


class PiperTTS(VoiceOutput):
    """Text-to-speech using Piper (ONNX-based, offline, natural voice)."""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self._piper = None
        self._sd = None
        self._np = None
        self._available = False

        try:
            from piper import PiperVoice
            import sounddevice as sd
            import numpy as np

            self._voice = PiperVoice.load(model_path)
            self._sd = sd
            self._np = np
            self._available = True
        except Exception:
            pass

    def is_available(self) -> bool:
        return self._available

    def speak(self, text: str) -> None:
        if not self._available:
            return

        try:
            # Synthesize to WAV in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_file:
                self._voice.synthesize(text, wav_file)

            # Read WAV data
            wav_buffer.seek(0)
            with wave.open(wav_buffer, "rb") as wav_file:
                sample_rate = wav_file.getframerate()
                frames = wav_file.readframes(wav_file.getnframes())
                audio = self._np.frombuffer(frames, dtype=self._np.int16).astype(self._np.float32) / 32768.0

            # Play audio
            self._sd.play(audio, samplerate=sample_rate)
            self._sd.wait()

        except Exception:
            pass
