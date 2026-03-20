"""Keyword-based sentiment analysis with intensity scoring."""

import re
from typing import Optional
from sol.memory.models import MoodEntry

# Mood keywords with intensity weights
MOOD_KEYWORDS = {
    "happy": {
        "ecstatic": 1.0, "overjoyed": 1.0, "thrilled": 0.9,
        "amazing": 0.8, "wonderful": 0.8, "fantastic": 0.8,
        "awesome": 0.7, "great": 0.7, "excited": 0.7,
        "happy": 0.6, "good": 0.5, "pleased": 0.5,
        "nice": 0.4, "okay": 0.3, "fine": 0.3,
        "good day": 0.6, "best day": 0.9,
    },
    "sad": {
        "devastated": 1.0, "heartbroken": 1.0, "miserable": 0.9,
        "depressed": 0.8, "hopeless": 0.8, "crushed": 0.8,
        "terrible": 0.7, "awful": 0.7, "crying": 0.7,
        "sad": 0.6, "unhappy": 0.6, "hurt": 0.6,
        "down": 0.5, "lonely": 0.5, "alone": 0.5,
        "bad day": 0.6, "not great": 0.4,
        "a bit sad": 0.3, "slightly down": 0.3,
    },
    "anxious": {
        "panicking": 1.0, "terrified": 0.9, "overwhelmed": 0.8,
        "stressed": 0.7, "anxious": 0.7, "worried": 0.6,
        "nervous": 0.6, "uneasy": 0.5, "tense": 0.5,
        "concerned": 0.4, "on edge": 0.5,
        "a bit worried": 0.3, "slightly nervous": 0.3,
    },
    "angry": {
        "furious": 1.0, "enraged": 1.0, "livid": 0.9,
        "outraged": 0.8, "pissed": 0.7, "angry": 0.7,
        "mad": 0.6, "frustrated": 0.6, "annoyed": 0.5,
        "irritated": 0.5, "bothered": 0.4,
        "a bit annoyed": 0.3,
    },
    "excited": {
        "mind blown": 1.0, "incredible": 0.9, "can't wait": 0.8,
        "so excited": 0.8, "pumped": 0.7, "stoked": 0.7,
        "excited": 0.6, "eager": 0.5, "looking forward": 0.5,
        "interested": 0.4, "curious": 0.3,
    },
}

# Intensity modifiers
AMPLIFIERS = {"very", "so", "really", "extremely", "super", "incredibly", "absolutely"}
DIMINISHERS = {"a bit", "a little", "slightly", "somewhat", "kind of", "sort of"}


def analyze_sentiment(text: str) -> Optional[MoodEntry]:
    """Analyze text and return a MoodEntry if emotional content is detected.

    Returns None if no strong emotional signal is found.
    """
    text_lower = text.lower().strip()

    best_mood = None
    best_intensity = 0.0
    best_keyword = None

    for mood, keywords in MOOD_KEYWORDS.items():
        # Check multi-word keywords first (longer matches take priority)
        sorted_keywords = sorted(keywords.keys(), key=len, reverse=True)
        for keyword in sorted_keywords:
            # Use word boundary matching to avoid partial matches (e.g. "mad" in "made")
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                intensity = keywords[keyword]

                # Apply modifiers
                for amp in AMPLIFIERS:
                    if f"{amp} {keyword}" in text_lower:
                        intensity = min(intensity + 0.2, 1.0)
                        break

                for dim in DIMINISHERS:
                    if f"{dim} {keyword}" in text_lower:
                        intensity = max(intensity - 0.2, 0.1)
                        break

                if intensity > best_intensity:
                    best_mood = mood
                    best_intensity = intensity
                    best_keyword = keyword

    if best_mood and best_intensity >= 0.3:
        return MoodEntry(
            mood=best_mood,
            intensity=round(best_intensity, 2),
            trigger=text[:100],
        )

    return None
