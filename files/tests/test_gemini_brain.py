"""Tests for Gemini cloud brain backend — all HTTP calls mocked."""

import json
import urllib.error
import pytest
from unittest.mock import patch, MagicMock

from sol.brain.gemini_brain import GeminiBrain


@pytest.fixture
def config():
    return {
        "brain": {
            "gemini_api_key": "test-key-123",
            "gemini_model": "gemini-2.5-flash",
            "gemini_url": "https://generativelanguage.googleapis.com/v1beta",
            "temperature": 0.7,
        }
    }


@pytest.fixture
def brain(memory_db, config):
    return GeminiBrain(memory_db, config)


def _mock_urlopen(response_data):
    """Create a mock urlopen response."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(response_data).encode("utf-8")
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


class TestGeminiBrainAvailability:
    """Test is_available() with mocked HTTP."""

    @patch("sol.brain.gemini_brain.socket.create_connection")
    @patch("urllib.request.urlopen")
    def test_available_with_key_and_internet(self, mock_open, mock_socket, brain):
        mock_socket.return_value = MagicMock()
        mock_open.return_value = _mock_urlopen({"name": "models/gemini-2.5-flash"})
        assert brain.is_available() is True

    @patch.dict("os.environ", {"GEMINI_API_KEY": ""}, clear=False)
    def test_unavailable_without_api_key(self, memory_db, tmp_path):
        # Use tmp_path as base_dir so no .env file is found
        brain = GeminiBrain(memory_db, {"_base_dir": str(tmp_path), "brain": {"gemini_api_key": ""}})
        assert brain.is_available() is False

    @patch("sol.brain.gemini_brain.socket.create_connection")
    def test_unavailable_without_internet(self, mock_socket, brain):
        mock_socket.side_effect = OSError("Network unreachable")
        assert brain.is_available() is False

    @patch("sol.brain.gemini_brain.socket.create_connection")
    @patch("urllib.request.urlopen")
    def test_unavailable_with_bad_key(self, mock_open, mock_socket, brain):
        mock_socket.return_value = MagicMock()
        mock_open.side_effect = urllib.error.HTTPError(
            "url", 403, "Forbidden", {}, None
        )
        assert brain.is_available() is False

    @patch("sol.brain.gemini_brain.socket.create_connection")
    @patch("urllib.request.urlopen")
    def test_caches_availability_result(self, mock_open, mock_socket, brain):
        mock_socket.return_value = MagicMock()
        mock_open.return_value = _mock_urlopen({"name": "models/gemini-2.5-flash"})
        brain.is_available()
        brain.is_available()
        # Socket + urlopen each called once due to caching
        assert mock_open.call_count == 1


class TestGeminiBrainThink:
    """Test think() with mocked HTTP."""

    @patch("urllib.request.urlopen")
    def test_generates_response(self, mock_open, brain):
        mock_open.return_value = _mock_urlopen({
            "candidates": [{
                "content": {
                    "parts": [{"text": "That's a cool goal. What's your first step?"}]
                }
            }]
        })
        response = brain.think("I want to start a business")
        assert "first step" in response.lower()

    @patch("urllib.request.urlopen")
    def test_stores_context(self, mock_open, brain):
        mock_open.return_value = _mock_urlopen({
            "candidates": [{
                "content": {"parts": [{"text": "Hello there!"}]}
            }]
        })
        brain.think("hi")
        ctx = brain.get_context()
        assert len(ctx) == 2
        assert ctx[0]["role"] == "human"
        assert ctx[0]["text"] == "hi"
        assert ctx[1]["role"] == "sol"

    @patch("urllib.request.urlopen")
    def test_handles_empty_response(self, mock_open, brain):
        mock_open.return_value = _mock_urlopen({"candidates": []})
        response = brain.think("hello")
        assert "blank" in response.lower() or "try again" in response.lower()

    @patch("urllib.request.urlopen")
    def test_handles_connection_error(self, mock_open, brain):
        mock_open.side_effect = urllib.error.URLError("Connection refused")
        response = brain.think("hello")
        assert "internet" in response.lower() or "connection" in response.lower()

    @patch("urllib.request.urlopen")
    def test_empty_input(self, mock_open, brain):
        response = brain.think("   ")
        assert "catch" in response.lower() or "again" in response.lower()
        mock_open.assert_not_called()

    @patch("urllib.request.urlopen")
    def test_sends_correct_payload(self, mock_open, brain):
        mock_open.return_value = _mock_urlopen({
            "candidates": [{
                "content": {"parts": [{"text": "Response"}]}
            }]
        })
        brain.think("test message")

        # Verify the request was made with correct structure
        call_args = mock_open.call_args
        request = call_args[0][0]
        payload = json.loads(request.data.decode("utf-8"))

        assert "system_instruction" in payload
        assert "contents" in payload
        assert "generationConfig" in payload
        assert payload["generationConfig"]["maxOutputTokens"] == 300


class TestGeminiBrainMemory:
    """Test memory operations during think()."""

    @patch("urllib.request.urlopen")
    def test_extracts_name(self, mock_open, brain, memory_db):
        mock_open.return_value = _mock_urlopen({
            "candidates": [{
                "content": {"parts": [{"text": "Nice to meet you, Alex!"}]}
            }]
        })
        brain.think("my name is Alex")
        assert memory_db.get_friend_name() == "Alex"

    @patch("urllib.request.urlopen")
    def test_extracts_preference(self, mock_open, brain, memory_db):
        mock_open.return_value = _mock_urlopen({
            "candidates": [{
                "content": {"parts": [{"text": "Pizza is solid. What's your go-to order?"}]}
            }]
        })
        brain.think("i like pizza")
        prefs = memory_db.get_preferences(limit=5)
        assert any(p["item"] == "pizza" for p in prefs)

    @patch("urllib.request.urlopen")
    def test_detects_mood(self, mock_open, brain, memory_db):
        mock_open.return_value = _mock_urlopen({
            "candidates": [{
                "content": {"parts": [{"text": "That sounds tough. What's going on?"}]}
            }]
        })
        brain.think("i feel really sad today")
        moods = memory_db.get_mood_history(limit=3)
        assert len(moods) > 0


class TestGeminiBrainConfig:
    """Test configuration handling."""

    def test_default_model(self, memory_db):
        brain = GeminiBrain(memory_db)
        assert brain.model == "gemini-2.5-flash"

    def test_custom_model(self, memory_db):
        brain = GeminiBrain(memory_db, {"brain": {"gemini_model": "gemini-2.5-pro"}})
        assert brain.model == "gemini-2.5-pro"

    def test_api_key_from_config(self, memory_db):
        brain = GeminiBrain(memory_db, {"brain": {"gemini_api_key": "my-key"}})
        assert brain.api_key == "my-key"

    @patch.dict("os.environ", {"GEMINI_API_KEY": "env-key"})
    def test_api_key_from_env(self, memory_db):
        brain = GeminiBrain(memory_db, {"brain": {"gemini_api_key": ""}})
        assert brain.api_key == "env-key"

    def test_config_key_takes_precedence_over_env(self, memory_db):
        import os
        with patch.dict("os.environ", {"GEMINI_API_KEY": "env-key"}):
            brain = GeminiBrain(memory_db, {"brain": {"gemini_api_key": "config-key"}})
            assert brain.api_key == "config-key"
