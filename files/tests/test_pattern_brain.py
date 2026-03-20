"""Tests for the pattern-matching brain."""

import pytest
from sol.brain.personality import GOODBYES, SAD_RESPONSES, HAPPY_RESPONSES, CONFUSED


class TestPatternBrain:

    def test_empty_input_returns_confused(self, pattern_brain):
        response = pattern_brain.think("")
        assert response in CONFUSED

    def test_greeting_first_meeting_no_name(self, pattern_brain):
        # No name set yet — brain should not crash
        response = pattern_brain.think("hello there")
        assert response  # Should return something

    def test_name_extraction_my_name_is(self, pattern_brain):
        response = pattern_brain.think("my name is Marvin")
        assert "Marvin" in response
        assert pattern_brain.memory.get_friend_name() == "Marvin"

    def test_name_extraction_im(self, pattern_brain):
        response = pattern_brain.think("i'm Alice")
        assert "Alice" in response
        assert pattern_brain.memory.get_friend_name() == "Alice"

    def test_name_extraction_call_me(self, pattern_brain):
        response = pattern_brain.think("call me Bob")
        assert "Bob" in response
        assert pattern_brain.memory.get_friend_name() == "Bob"

    def test_goodbye_triggers(self, pattern_brain):
        response = pattern_brain.think("goodbye")
        assert response in GOODBYES

    def test_sad_detection(self, pattern_brain):
        response = pattern_brain.think("i feel really sad today")
        assert response in SAD_RESPONSES

    def test_happy_detection(self, pattern_brain):
        pattern_brain.memory.set_friend_name("Test")  # Set name first to avoid name extraction
        response = pattern_brain.think("i'm so happy right now")
        assert response in HAPPY_RESPONSES

    def test_fact_extraction(self, pattern_brain):
        pattern_brain.memory.set_friend_name("Test")
        response = pattern_brain.think("i work as a software engineer at google")
        assert "noted" in response.lower() or "work" in response.lower()
        facts = pattern_brain.memory.get_facts()
        assert len(facts) == 1
        assert "work as" in facts[0].lower()

    def test_like_preference(self, pattern_brain):
        response = pattern_brain.think("i like pizza")
        assert "pizza" in response
        prefs = pattern_brain.memory.get_preferences()
        assert any(p["item"] == "pizza" and p["sentiment"] == "like" for p in prefs)

    def test_dislike_preference(self, pattern_brain):
        response = pattern_brain.think("i hate spiders")
        assert "spiders" in response
        prefs = pattern_brain.memory.get_preferences()
        assert any(p["item"] == "spiders" and p["sentiment"] == "dislike" for p in prefs)

    def test_who_are_you(self, pattern_brain):
        response = pattern_brain.think("who are you")
        assert "SOL" in response

    def test_how_are_you(self, pattern_brain):
        response = pattern_brain.think("how are you")
        assert response  # Should return a meaningful response

    def test_recall_empty_memory(self, pattern_brain):
        response = pattern_brain.think("what do you remember")
        assert "don't know much" in response.lower() or "tell me" in response.lower()

    def test_recall_with_facts(self, pattern_brain):
        pattern_brain.memory.set_friend_name("Marvin")
        pattern_brain.memory.add_fact("I am a programmer")
        response = pattern_brain.think("what do you remember about me")
        assert "Marvin" in response
        assert "programmer" in response.lower()

    def test_joke(self, pattern_brain):
        response = pattern_brain.think("tell me a joke")
        assert response  # Should return a joke from the JOKES list

    def test_time_question(self, pattern_brain):
        response = pattern_brain.think("what time is it")
        assert "AM" in response or "PM" in response

    def test_thank_you(self, pattern_brain):
        pattern_brain.memory.set_friend_name("Test")
        response = pattern_brain.think("thank you sol")
        assert "help" in response.lower() or "Test" in response

    def test_context_grows(self, pattern_brain):
        pattern_brain.think("hello")
        pattern_brain.think("how is the weather")
        pattern_brain.think("i like sunny days")
        assert len(pattern_brain.context) == 3

    def test_is_available(self, pattern_brain):
        assert pattern_brain.is_available() is True
