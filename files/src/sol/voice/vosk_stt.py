"""Vosk-based speech-to-text — offline, lightweight."""

import os
import json
import queue

from sol.voice.base import VoiceInput


class VoskSTT(VoiceInput):
    """Speech-to-text using Vosk (offline, Kaldi-based)."""

    def __init__(self, model_path: str, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.audio_queue = queue.Queue()
        self.model = None
        self.recognizer = None
        self._sd = None
        self._available = False

        try:
            import vosk
            import sounddevice as sd
            self._sd = sd
            vosk.SetLogLevel(-1)
            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            self._available = True
        except Exception:
            pass

    def is_available(self) -> bool:
        return self._available

    def _audio_callback(self, indata, frames, time_info, status):
        self.audio_queue.put(bytes(indata))

    def listen(self) -> str:
        if not self._available or not self._sd:
            return ""

        try:
            with self._sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=self._audio_callback,
            ):
                silence_count = 0
                has_speech = False

                while True:
                    data = self.audio_queue.get()

                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "").strip()
                        if text:
                            return text
                        silence_count += 1
                    else:
                        partial = json.loads(self.recognizer.PartialResult())
                        if partial.get("partial", "").strip():
                            has_speech = True
                            silence_count = 0

                    if has_speech and silence_count > 3:
                        final = json.loads(self.recognizer.FinalResult())
                        text = final.get("text", "").strip()
                        if text:
                            return text
                        break

        except Exception:
            pass

        return ""

    @staticmethod
    def find_model(base_dir: str):
        """Search common paths for a Vosk model directory."""
        candidates = [
            os.path.join(base_dir, "models", "vosk-model-small-en-us-0.15"),
            os.path.join(base_dir, "model"),
            os.path.join(base_dir, "vosk-model-small-en-us-0.15"),
        ]
        for c in candidates:
            if os.path.isdir(c):
                return c
        return None
