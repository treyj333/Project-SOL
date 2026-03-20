"""Tests for JSON to SQLite migration."""

import os
import json
import pytest
from sol.memory.migration import maybe_migrate
from sol.memory.sqlite_store import SqliteMemoryStore


class TestMigration:

    def test_migration_creates_db(self, sample_json_file, tmp_path):
        db_path = str(tmp_path / "sol_memory.db")
        result = maybe_migrate(sample_json_file, db_path)
        assert result is True
        assert os.path.exists(db_path)

    def test_migration_preserves_name(self, sample_json_file, tmp_path):
        db_path = str(tmp_path / "sol_memory.db")
        maybe_migrate(sample_json_file, db_path)
        store = SqliteMemoryStore(db_path)
        assert store.get_friend_name() == "Marvin"
        store.close()

    def test_migration_preserves_facts(self, sample_json_file, tmp_path):
        db_path = str(tmp_path / "sol_memory.db")
        maybe_migrate(sample_json_file, db_path)
        store = SqliteMemoryStore(db_path)
        facts = store.get_facts(limit=99)
        assert "I am a programmer" in facts
        assert "I live in california" in facts
        store.close()

    def test_migration_parses_dislikes(self, sample_json_file, tmp_path):
        db_path = str(tmp_path / "sol_memory.db")
        maybe_migrate(sample_json_file, db_path)
        store = SqliteMemoryStore(db_path)
        prefs = store.get_preferences(limit=99)
        assert any(p["item"] == "coffee" and p["sentiment"] == "like" for p in prefs)
        assert any(p["item"] == "loud music" and p["sentiment"] == "dislike" for p in prefs)
        store.close()

    def test_migration_preserves_conversations(self, sample_json_file, tmp_path):
        db_path = str(tmp_path / "sol_memory.db")
        maybe_migrate(sample_json_file, db_path)
        store = SqliteMemoryStore(db_path)
        assert store.get_conversations_count() == 15
        store.close()

    def test_migration_preserves_timestamps(self, sample_json_file, tmp_path):
        db_path = str(tmp_path / "sol_memory.db")
        maybe_migrate(sample_json_file, db_path)
        store = SqliteMemoryStore(db_path)
        assert store.get_first_met() == "2026-01-01T10:00:00"
        assert store.get_last_talked() == "2026-03-19T20:00:00"
        store.close()

    def test_migration_creates_backup(self, sample_json_file, tmp_path):
        db_path = str(tmp_path / "sol_memory.db")
        maybe_migrate(sample_json_file, db_path)
        assert os.path.exists(sample_json_file + ".backup")

    def test_migration_skips_if_db_exists(self, sample_json_file, tmp_path):
        db_path = str(tmp_path / "sol_memory.db")
        # Create empty db first
        with open(db_path, "w") as f:
            f.write("")
        result = maybe_migrate(sample_json_file, db_path)
        assert result is False

    def test_migration_skips_if_no_json(self, tmp_path):
        json_path = str(tmp_path / "nonexistent.json")
        db_path = str(tmp_path / "sol_memory.db")
        result = maybe_migrate(json_path, db_path)
        assert result is False

    def test_migration_handles_corrupt_json(self, tmp_path):
        json_path = str(tmp_path / "corrupt.json")
        with open(json_path, "w") as f:
            f.write("{invalid json")
        db_path = str(tmp_path / "sol_memory.db")
        result = maybe_migrate(json_path, db_path)
        assert result is False
        # DB should be cleaned up
        assert not os.path.exists(db_path)

    def test_migration_preserves_topics(self, sample_json_file, tmp_path):
        db_path = str(tmp_path / "sol_memory.db")
        maybe_migrate(sample_json_file, db_path)
        store = SqliteMemoryStore(db_path)
        topics = store.get_topics(limit=99)
        assert "programming" in topics
        assert "space" in topics
        assert "music" in topics
        store.close()
