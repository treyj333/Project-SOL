"""Tests for the SQLite memory store."""

import pytest
from sol.memory.sqlite_store import SqliteMemoryStore


class TestSqliteMemoryStore:

    def test_friend_name(self, memory_db):
        assert memory_db.get_friend_name() is None
        memory_db.set_friend_name("Alex")
        assert memory_db.get_friend_name() == "Alex"

    def test_add_and_get_facts(self, memory_db):
        memory_db.add_fact("I am a programmer")
        memory_db.add_fact("I live in California")
        facts = memory_db.get_facts()
        assert len(facts) == 2
        assert "I am a programmer" in facts

    def test_duplicate_fact_ignored(self, memory_db):
        memory_db.add_fact("I am a programmer")
        memory_db.add_fact("I am a programmer")
        facts = memory_db.get_facts()
        assert len(facts) == 1

    def test_fact_categories(self, memory_db):
        memory_db.add_fact("I work at Google", category="work")
        memory_db.add_fact("I have a dog", category="family")
        work_facts = memory_db.get_facts(category="work")
        assert len(work_facts) == 1
        assert "Google" in work_facts[0]

    def test_preferences(self, memory_db):
        memory_db.add_preference("coffee", "like")
        memory_db.add_preference("spiders", "dislike")
        prefs = memory_db.get_preferences()
        assert len(prefs) == 2
        assert any(p["item"] == "coffee" and p["sentiment"] == "like" for p in prefs)
        assert any(p["item"] == "spiders" and p["sentiment"] == "dislike" for p in prefs)

    def test_duplicate_preference_ignored(self, memory_db):
        memory_db.add_preference("coffee", "like")
        memory_db.add_preference("coffee", "like")
        prefs = memory_db.get_preferences()
        assert len(prefs) == 1

    def test_mood_history(self, memory_db):
        memory_db.add_mood("happy", 0.7, "good news")
        memory_db.add_mood("sad", 0.5, "bad day")
        moods = memory_db.get_mood_history()
        assert len(moods) == 2
        assert moods[0]["mood"] == "happy"
        assert moods[1]["mood"] == "sad"

    def test_topics(self, memory_db):
        memory_db.add_topic("programming")
        memory_db.add_topic("music")
        memory_db.add_topic("programming")  # Should increment count
        topics = memory_db.get_topics()
        assert "programming" in topics
        assert "music" in topics

    def test_conversations_count(self, memory_db):
        assert memory_db.get_conversations_count() == 0
        memory_db.increment_conversations()
        assert memory_db.get_conversations_count() == 1
        memory_db.increment_conversations()
        assert memory_db.get_conversations_count() == 2

    def test_timestamps(self, memory_db):
        assert memory_db.get_first_met() is None
        memory_db.set_first_met("2026-01-01T10:00:00")
        assert memory_db.get_first_met() == "2026-01-01T10:00:00"

        assert memory_db.get_last_talked() is None
        memory_db.set_last_talked("2026-03-20T15:00:00")
        assert memory_db.get_last_talked() == "2026-03-20T15:00:00"

    def test_metadata(self, memory_db):
        memory_db.set_friend_name("Alex")
        memory_db.add_fact("test fact")
        memory_db.add_preference("coffee", "like")
        memory_db.increment_conversations()

        meta = memory_db.get_metadata()
        assert meta["friend_name"] == "Alex"
        assert meta["facts_count"] == 1
        assert meta["prefs_count"] == 1
        assert meta["conversations"] == 1
        assert "relationship_depth" in meta

    def test_conversation_summary(self, memory_db):
        memory_db.add_conversation_summary(1, "Test summary", 5, "positive", "coding")
        summaries = memory_db.get_recent_summaries()
        assert len(summaries) == 1
        assert summaries[0]["summary"] == "Test summary"

    def test_journal_entry(self, memory_db):
        memory_db.add_journal_entry("Today was a good day", "", "happy")
        entries = memory_db.get_journal_entries()
        assert len(entries) == 1
        assert "good day" in entries[0]["content"]

    def test_reminders(self, memory_db):
        memory_db.add_reminder("Call mom", "2026-01-01T10:00:00")
        pending = memory_db.get_pending_reminders()
        assert len(pending) == 1
        memory_db.complete_reminder(pending[0]["id"])
        pending = memory_db.get_pending_reminders()
        assert len(pending) == 0

    def test_notes(self, memory_db):
        memory_db.add_note("Dentist on March 25th", "health")
        results = memory_db.search_notes("dentist")
        assert len(results) >= 1

    def test_search_facts(self, memory_db):
        memory_db.add_fact("I am a software engineer")
        memory_db.add_fact("I like hiking in mountains")
        results = memory_db.search_facts("engineer")
        assert len(results) >= 1

    def test_supports_feature(self, memory_db):
        assert memory_db.supports_feature("journal") is True
        assert memory_db.supports_feature("reminders") is True
        assert memory_db.supports_feature("notes") is True
        assert memory_db.supports_feature("summaries") is True
        assert memory_db.supports_feature("flying") is False

    def test_last_mood(self, memory_db):
        assert memory_db.get_last_mood() is None
        memory_db.add_mood("happy", 0.8)
        last = memory_db.get_last_mood()
        assert last["mood"] == "happy"
        assert last["intensity"] == 0.8
