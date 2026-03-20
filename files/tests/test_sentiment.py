"""Tests for sentiment analysis."""

import pytest
from sol.brain.sentiment import analyze_sentiment


class TestSentiment:

    def test_detect_happy(self):
        result = analyze_sentiment("I'm so happy today!")
        assert result is not None
        assert result.mood == "happy"
        assert result.intensity >= 0.5

    def test_detect_sad(self):
        result = analyze_sentiment("I feel really sad")
        assert result is not None
        assert result.mood == "sad"

    def test_detect_angry(self):
        result = analyze_sentiment("I'm so frustrated with this")
        assert result is not None
        assert result.mood == "angry"

    def test_detect_anxious(self):
        result = analyze_sentiment("I'm feeling really stressed and worried")
        assert result is not None
        assert result.mood in ("anxious",)

    def test_detect_excited(self):
        result = analyze_sentiment("I can't wait for tomorrow!")
        assert result is not None
        assert result.mood == "excited"

    def test_neutral_returns_none(self):
        result = analyze_sentiment("The table is made of wood")
        assert result is None

    def test_amplifier_increases_intensity(self):
        normal = analyze_sentiment("I feel sad")
        amplified = analyze_sentiment("I feel very sad")
        assert amplified is not None
        assert normal is not None
        assert amplified.intensity >= normal.intensity

    def test_diminisher_decreases_intensity(self):
        normal = analyze_sentiment("I'm worried")
        diminished = analyze_sentiment("I'm a bit worried")
        # Both should detect something, diminished should be lower
        assert normal is not None
        assert diminished is not None
        assert diminished.intensity <= normal.intensity

    def test_trigger_captured(self):
        result = analyze_sentiment("I'm devastated about losing my job")
        assert result is not None
        assert result.trigger is not None
        assert "devastated" in result.trigger

    def test_high_intensity_words(self):
        result = analyze_sentiment("I'm absolutely devastated")
        assert result is not None
        assert result.intensity >= 0.8

    def test_low_intensity_words(self):
        result = analyze_sentiment("Things are okay I guess")
        # "okay" is low intensity
        assert result is None or result.intensity <= 0.4
