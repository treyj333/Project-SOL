"""Tests for macOS native TTS backend."""

import sys
import pytest
from unittest.mock import patch, MagicMock

from sol.voice.mac_say_tts import MacSayTTS


class TestMacSayTTS:

    @patch("sol.voice.mac_say_tts.shutil.which", return_value="/usr/bin/say")
    @patch("sol.voice.mac_say_tts.sys")
    def test_available_on_macos(self, mock_sys, mock_which):
        mock_sys.platform = "darwin"
        tts = MacSayTTS()
        assert tts.is_available() is True

    @patch("sol.voice.mac_say_tts.shutil.which", return_value="/usr/bin/say")
    @patch("sol.voice.mac_say_tts.sys")
    def test_unavailable_on_linux(self, mock_sys, mock_which):
        mock_sys.platform = "linux"
        tts = MacSayTTS()
        assert tts.is_available() is False

    @patch("sol.voice.mac_say_tts.shutil.which", return_value=None)
    @patch("sol.voice.mac_say_tts.sys")
    def test_unavailable_without_say_command(self, mock_sys, mock_which):
        mock_sys.platform = "darwin"
        tts = MacSayTTS()
        assert tts.is_available() is False

    @patch("sol.voice.mac_say_tts.subprocess.run")
    @patch("sol.voice.mac_say_tts.shutil.which", return_value="/usr/bin/say")
    @patch("sol.voice.mac_say_tts.sys")
    def test_speak_calls_say_command(self, mock_sys, mock_which, mock_run):
        mock_sys.platform = "darwin"
        tts = MacSayTTS(voice="Samantha", rate=180)
        tts.speak("Hello friend")
        mock_run.assert_called_once_with(
            ["say", "-v", "Samantha", "-r", "180", "Hello friend"],
            check=False,
            timeout=30,
        )

    @patch("sol.voice.mac_say_tts.subprocess.run")
    @patch("sol.voice.mac_say_tts.shutil.which", return_value="/usr/bin/say")
    @patch("sol.voice.mac_say_tts.sys")
    def test_speak_empty_text_does_nothing(self, mock_sys, mock_which, mock_run):
        mock_sys.platform = "darwin"
        tts = MacSayTTS()
        tts.speak("")
        mock_run.assert_not_called()

    def test_custom_voice_and_rate(self):
        tts = MacSayTTS(voice="Alex", rate=200)
        assert tts.voice == "Alex"
        assert tts.rate == 200
