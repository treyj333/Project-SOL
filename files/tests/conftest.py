"""Shared test fixtures for SOL tests."""

import os
import sys
import json
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sol.memory.sqlite_store import SqliteMemoryStore
from sol.memory.json_store import JsonMemoryStore
from sol.brain.pattern_brain import PatternBrain


@pytest.fixture
def memory_db():
    """In-memory SQLite store for testing."""
    store = SqliteMemoryStore(":memory:")
    return store


@pytest.fixture
def json_memory(tmp_path):
    """JSON memory store using a temp file."""
    path = str(tmp_path / "sol_memory.json")
    return JsonMemoryStore(path)


@pytest.fixture
def sample_json_file(tmp_path):
    """Create a sample sol_memory.json for migration tests."""
    data = {
        "friend_name": "Alex",
        "facts": ["I am a programmer", "I live in california"],
        "preferences": ["coffee", "NOT loud music"],
        "conversations": 15,
        "first_met": "2026-01-01T10:00:00",
        "last_talked": "2026-03-19T20:00:00",
        "mood_history": [{"mood": "happy", "time": "2026-03-19T20:05:00"}],
        "topics": ["programming", "space", "music"],
    }
    path = tmp_path / "sol_memory.json"
    path.write_text(json.dumps(data))
    return str(path)


@pytest.fixture
def pattern_brain(memory_db):
    """Pattern brain with in-memory SQLite store."""
    return PatternBrain(memory_db)
