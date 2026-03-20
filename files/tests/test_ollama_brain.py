"""Tests for Ollama brain backend — all HTTP calls mocked."""

import json
import urllib.error
import pytest
from unittest.mock import patch, MagicMock

from sol.brain.ollama_brain import OllamaBrain


@pytest.fixture
def config():
    return {
        "brain": {
            "ollama_model": "llama3.2:1b",
            "ollama_url": "http://localhost:11434",
            "temperature": 0.7,
        }
    }


@pytest.fixture
def brain(memory_db, config):
    return OllamaBrain(memory_db, config)


def _mock_urlopen(response_data):
    """Create a mock urlopen response."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(response_data).encode("utf-8")
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


class TestOllamaBrainAvailability:
    """Test is_available() with mocked HTTP."""

    @patch("urllib.request.urlopen")
    def test_available_when_model_exists(self, mock_open, brain):
        mock_open.return_value = _mock_urlopen({
            "models": [{"name": "llama3.2:1b"}]
        })
        assert brain.is_available() is True

    @patch("urllib.request.urlopen")
    def test_unavailable_when_model_missing(self, mock_open, brain):
        mock_open.return_value = _mock_urlopen({
            "models": [{"name": "mistral:7b"}]
        })
        assert brain.is_available() is False

    @patch("urllib.request.urlopen")
    def test_unavailable_when_ollama_not_running(self, mock_open, brain):
        mock_open.side_effect = urllib.error.URLError("Connection refused")
        assert brain.is_available() is False

    @patch("urllib.request.urlopen")
    def test_caches_availability_result(self, mock_open, brain):
        mock_open.return_value = _mock_urlopen({
            "models": [{"name": "llama3.2:1b"}]
        })
        brain.is_available()
        brain.is_available()
        assert mock_open.call_count == 1


class TestOllamaBrainThink:
    """Test think() with mocked HTTP."""

    @patch("urllib.request.urlopen")
    def test_generates_response(self, mock_open, brain):
        mock_open.return_value = _mock_urlopen({
            "message": {"content": "SOL happy to meet friend! What is name?"}
        })
        response = brain.think("hello there")
        assert "SOL" in response

    @patch("urllib.request.urlopen")
    def test_stores_context(self, mock_open, brain):
        mock_open.return_value = _mock_urlopen({
            "message": {"content": "Hello friend!"}
        })
        brain.think("hi sol")
        ctx = brain.get_context()
        assert len(ctx) == 2
        assert ctx[0]["role"] == "human"
        assert ctx[0]["text"] == "hi sol"
        assert ctx[1]["role"] == "sol"

    @patch("urllib.request.urlopen")
    def test_handles_empty_response(self, mock_open, brain):
        mock_open.return_value = _mock_urlopen({
            "message": {"content": ""}
        })
        response = brain.think("hello")
        assert "try again" in response.lower()

    @patch("urllib.request.urlopen")
    def test_handles_connection_error(self, mock_open, brain):
        mock_open.side_effect = urllib.error.URLError("Connection refused")
        response = brain.think("hello")
        assert "Ollama" in response

    @patch("urllib.request.urlopen")
    def test_empty_input(self, mock_open, brain):
        response = brain.think("   ")
        assert "catch" in response.lower() or "again" in response.lower()
        mock_open.assert_not_called()


class TestOllamaBrainMemory:
    """Test memory operations during think()."""

    @patch("urllib.request.urlopen")
    def test_extracts_name(self, mock_open, brain, memory_db):
        mock_open.return_value = _mock_urlopen({
            "message": {"content": "SOL happy to know Alex!"}
        })
        brain.think("my name is Alex")
        assert memory_db.get_friend_name() == "Alex"

    @patch("urllib.request.urlopen")
    def test_extracts_preference(self, mock_open, brain, memory_db):
        mock_open.return_value = _mock_urlopen({
            "message": {"content": "SOL learn new thing! Pizza good!"}
        })
        brain.think("i like pizza")
        prefs = memory_db.get_preferences(limit=5)
        assert any(p["item"] == "pizza" for p in prefs)

    @patch("urllib.request.urlopen")
    def test_detects_mood(self, mock_open, brain, memory_db):
        mock_open.return_value = _mock_urlopen({
            "message": {"content": "SOL sorry friend sad."}
        })
        brain.think("i feel really sad today")
        moods = memory_db.get_mood_history(limit=3)
        assert len(moods) > 0


class TestOllamaBrainConfig:
    """Test configuration handling."""

    def test_default_model(self, memory_db):
        brain = OllamaBrain(memory_db)
        assert brain.model == "llama3.2:1b"

    def test_custom_model(self, memory_db):
        brain = OllamaBrain(memory_db, {"brain": {"ollama_model": "mistral:7b"}})
        assert brain.model == "mistral:7b"

    def test_custom_url(self, memory_db):
        brain = OllamaBrain(memory_db, {"brain": {"ollama_url": "http://192.168.1.10:11434"}})
        assert brain.base_url == "http://192.168.1.10:11434"
