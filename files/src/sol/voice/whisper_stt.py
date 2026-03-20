"""Whisper.cpp-based speech-to-text — higher accuracy, offline."""

import os
import tempfile
import wave
import struct
from sol.voice.base import VoiceInput


class WhisperSTT(VoiceInput):
    """Speech-to-text using whisper-cpp-python (offline, high accuracy)."""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self._whisper = None
        self._sd = None
        self._np = None
        self._available = False
        self.sample_rate = 16000

        try:
            from whisper_cpp_python import Whisper
            import sounddevice as sd
            import numpy as np

            self._whisper = Whisper(model_path=model_path)
            self._sd = sd
            self._np = np
            self._available = True
        except Exception:
            pass

    def is_available(self) -> bool:
        return self._available

    def listen(self) -> str:
        if not self._available:
            return ""

        try:
            # Record audio until silence
            duration = 10  # max seconds
            recording = self._sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
            )
            self._sd.wait()

            # Trim silence from end
            audio = recording.flatten()
            threshold = 0.01
            nonsilent = self._np.where(self._np.abs(audio) > threshold)[0]
            if len(nonsilent) == 0:
                return ""
            audio = audio[: nonsilent[-1] + self.sample_rate]  # keep 1s after last sound

            # Transcribe
            result = self._whisper.transcribe(audio)
            text = result.get("text", "").strip()
            return text

        except Exception:
            pass

        return ""
