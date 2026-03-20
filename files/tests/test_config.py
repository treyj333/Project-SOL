"""Tests for configuration loading."""

import os
import pytest
from sol.config import load_config, get, resolve_path, DEFAULTS


class TestConfig:

    def test_default_config(self, tmp_path):
        config = load_config(str(tmp_path))
        assert get(config, "general.mode") == "cli"
        assert get(config, "brain.backend") == "auto"
        assert get(config, "memory.backend") == "sqlite"

    def test_get_nested_key(self, tmp_path):
        config = load_config(str(tmp_path))
        assert get(config, "voice.speech_rate") == 140
        assert get(config, "plugins.enabled") is True

    def test_get_missing_key_returns_default(self, tmp_path):
        config = load_config(str(tmp_path))
        assert get(config, "nonexistent.key", "fallback") == "fallback"

    def test_resolve_relative_path(self, tmp_path):
        config = {"_base_dir": str(tmp_path)}
        result = resolve_path(config, "models/test.gguf")
        assert result == os.path.join(str(tmp_path), "models/test.gguf")

    def test_resolve_absolute_path(self, tmp_path):
        config = {"_base_dir": str(tmp_path)}
        result = resolve_path(config, "/absolute/path.gguf")
        assert result == "/absolute/path.gguf"

    def test_toml_override(self, tmp_path):
        # Create a minimal sol.toml
        toml_content = b'[brain]\nbackend = "pattern"\n'
        (tmp_path / "sol.toml").write_bytes(toml_content)

        config = load_config(str(tmp_path))
        assert get(config, "brain.backend") == "pattern"
        # Other defaults should still be present
        assert get(config, "general.mode") == "cli"

    def test_base_dir_stored(self, tmp_path):
        config = load_config(str(tmp_path))
        assert config["_base_dir"] == str(tmp_path)
