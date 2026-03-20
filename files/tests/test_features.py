"""Tests for daily utility features — journal, reminders, notes."""

import pytest
from sol.features.journal import is_journal_trigger, get_journal_prompt, generate_session_summary
from sol.features.reminders import is_reminder_trigger, parse_reminder
from sol.features.notes import is_note_trigger, is_recall_trigger, extract_note, extract_recall_query


class TestJournal:

    def test_journal_trigger(self):
        assert is_journal_trigger("let's journal") is True
        assert is_journal_trigger("tell you about my day") is True
        assert is_journal_trigger("hello there") is False

    def test_journal_prompts(self):
        prompt = get_journal_prompt(0)
        assert prompt is not None
        assert "SOL" in prompt

        prompt = get_journal_prompt(99)
        assert prompt is None

    def test_session_summary(self, memory_db):
        context = [
            {"role": "human", "text": "hello there sol"},
            {"role": "human", "text": "i like programming today"},
            {"role": "human", "text": "goodbye"},
        ]
        memory_db.increment_conversations()
        generate_session_summary(context, memory_db)
        summaries = memory_db.get_recent_summaries()
        assert len(summaries) == 1
        assert "3 exchanges" in summaries[0]["summary"]


class TestReminders:

    def test_reminder_trigger(self):
        assert is_reminder_trigger("remind me to call mom") is True
        assert is_reminder_trigger("don't let me forget the meeting") is True
        assert is_reminder_trigger("hello sol") is False

    def test_parse_reminder_with_time(self):
        result = parse_reminder("remind me to call mom tomorrow")
        assert result is not None
        assert "call mom" in result["content"]
        assert result["trigger_at"] is not None

    def test_parse_reminder_in_hours(self):
        result = parse_reminder("remind me to check email in 2 hours")
        assert result is not None
        assert "check email" in result["content"]

    def test_parse_reminder_no_time(self):
        result = parse_reminder("remind me to buy groceries")
        assert result is not None
        assert "buy groceries" in result["content"]
        # Should default to 1 hour from now

    def test_parse_empty_reminder(self):
        result = parse_reminder("remind me to")
        assert result is None


class TestNotes:

    def test_note_trigger(self):
        assert is_note_trigger("remember that my dentist is on Tuesday") is True
        assert is_note_trigger("note that the meeting is at 3pm") is True
        assert is_note_trigger("hello there") is False

    def test_recall_trigger(self):
        assert is_recall_trigger("what did i tell you about the dentist") is True
        assert is_recall_trigger("find my note about meetings") is True
        assert is_recall_trigger("hello") is False

    def test_extract_note(self):
        note = extract_note("remember that my dentist appointment is on Tuesday")
        assert note is not None
        assert "dentist" in note

    def test_extract_recall_query(self):
        query = extract_recall_query("what did i tell you about the dentist")
        assert query is not None
        assert "dentist" in query

    def test_extract_empty_note(self):
        note = extract_note("remember that")
        assert note is None
