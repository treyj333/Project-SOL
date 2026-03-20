"""Configuration loading for SOL — reads sol.toml with sensible defaults."""

import os

# Default configuration
DEFAULTS = {
    "general": {
        "mode": "cli",
        "voice_input": True,
        "voice_output": True,
        "data_dir": ".",
    },
    "brain": {
        "backend": "auto",
        "gemini_api_key": "",
        "gemini_model": "gemini-2.5-flash",
        "gemini_url": "https://generativelanguage.googleapis.com/v1beta",
        "ollama_model": "gemma3:4b",
        "ollama_url": "http://localhost:11434",
        "llm_model": "models/llm/tinyllama-1.1b-chat.Q4_K_M.gguf",
        "llm_context_length": 2048,
        "llm_threads": 4,
        "temperature": 0.7,
    },
    "voice": {
        "stt_backend": "auto",
        "tts_backend": "auto",
        "wake_word": False,
        "wake_phrase": "hey sol",
        "speech_rate": 140,
        "vosk_model": "models/vosk-model-small-en-us-0.15",
        "whisper_model": "models/whisper-small.bin",
        "piper_model": "models/piper/en_US-lessac-medium.onnx",
    },
    "memory": {
        "backend": "sqlite",
    },
    "features": {
        "journal": True,
        "reminders": True,
        "notes": True,
    },
    "plugins": {
        "enabled": True,
        "directory": "plugins",
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, recursively for nested dicts."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _load_toml(path: str) -> dict:
    """Load a TOML file, trying tomllib (3.11+) then tomli, then basic parsing."""
    try:
        import tomllib
        with open(path, "rb") as f:
            return tomllib.load(f)
    except ImportError:
        pass

    try:
        import tomli
        with open(path, "rb") as f:
            return tomli.load(f)
    except ImportError:
        pass

    # Minimal fallback: just return empty and use defaults
    return {}


def load_config(base_dir: str, config_filename: str = "sol.toml") -> dict:
    """Load configuration from sol.toml, merged with defaults.

    Args:
        base_dir: The directory containing sol.toml and other SOL files.
        config_filename: Name of the config file.

    Returns:
        Merged configuration dict.
    """
    config = DEFAULTS.copy()
    config_path = os.path.join(base_dir, config_filename)

    if os.path.exists(config_path):
        user_config = _load_toml(config_path)
        config = _deep_merge(DEFAULTS, user_config)

    # Store base_dir for resolving relative paths
    config["_base_dir"] = base_dir

    return config


def get(config: dict, key: str, default=None):
    """Get a nested config value using dot notation. e.g. get(config, 'brain.backend')"""
    keys = key.split(".")
    value = config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    return value


def resolve_path(config: dict, relative_path: str) -> str:
    """Resolve a relative path against the base directory."""
    base = config.get("_base_dir", ".")
    if os.path.isabs(relative_path):
        return relative_path
    return os.path.join(base, relative_path)
