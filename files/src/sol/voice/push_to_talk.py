"""Push-to-talk wrapper — press space to record, auto-stops on silence."""

import json
import sys
import select
import queue

from sol.voice.base import VoiceInput


def _is_unix():
    """Check if we're on a Unix-like system with terminal control."""
    try:
        import termios
        return sys.stdin.isatty()
    except ImportError:
        return False


class PushToTalk(VoiceInput):
    """Wraps a Vosk STT backend with push-to-talk.

    The mic stays OFF until you press space. Once pressed, it records
    until you stop talking (silence detection), then returns the text.
    Press space again for the next message.
    """

    def __init__(self, stt_backend, sample_rate: int = 16000):
        self.stt = stt_backend
        self.sample_rate = sample_rate
        self._available = _is_unix() and stt_backend.is_available()

    def is_available(self) -> bool:
        return self._available

    def listen(self) -> str:
        """Wait for space, then record until silence."""
        if not self._available:
            return ""

        # Wait for space key
        if not self._wait_for_key():
            return ""

        # Now record with silence detection
        return self._record_until_silence()

    def _wait_for_key(self) -> bool:
        """Wait for space bar press. Returns False on Ctrl+C."""
        import termios
        import tty

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            while True:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    ch = sys.stdin.read(1)
                    if ch == ' ':
                        return True
                    if ch == '\x03':  # Ctrl+C
                        raise KeyboardInterrupt
                    if ch == '\n' or ch == '\r':  # Enter also works
                        return True
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def _record_until_silence(self) -> str:
        """Record audio and stop when silence is detected."""
        import sounddevice as sd

        audio_queue = queue.Queue()
        recognizer = self.stt.recognizer
        recognizer.Reset()

        def callback(indata, frames, time_info, status):
            audio_queue.put(bytes(indata))

        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=4000,
                dtype="int16",
                channels=1,
                callback=callback,
            ):
                silence_count = 0
                has_speech = False

                while True:
                    data = audio_queue.get(timeout=5)

                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "").strip()
                        if text:
                            return text
                        silence_count += 1
                    else:
                        partial = json.loads(recognizer.PartialResult())
                        if partial.get("partial", "").strip():
                            has_speech = True
                            silence_count = 0

                    # Stop after speech followed by silence
                    if has_speech and silence_count > 3:
                        final = json.loads(recognizer.FinalResult())
                        return final.get("text", "").strip()

                    # Timeout if no speech at all after a while
                    if not has_speech and silence_count > 10:
                        return ""

        except queue.Empty:
            # Timeout waiting for audio
            final = json.loads(recognizer.FinalResult())
            return final.get("text", "").strip()
        except Exception:
            return ""
