"""Emotional intelligence — relationship depth, proactive check-ins, adaptive personality."""

from typing import Optional
from sol.memory.base import MemoryStore


def get_proactive_checkin(memory: MemoryStore) -> str:
    """Generate a proactive emotional check-in based on last mood.

    Called at session start. Returns empty string if no check-in needed.
    """
    try:
        moods = memory.get_mood_history(limit=1)
        if not moods:
            return ""

        last_mood = moods[-1]
        mood = last_mood.get("mood", "")
        trigger = last_mood.get("trigger", "")

        if mood in ("sad", "anxious", "angry"):
            if trigger:
                snippet = trigger[:40].strip()
                return f"Last time you seemed {mood} when you mentioned '{snippet}'. How's that going?"
            else:
                return f"You seemed {mood} last time we talked. Everything alright?"

    except Exception:
        pass

    return ""


def get_personality_modifier(memory: MemoryStore) -> dict:
    """Return personality parameters based on relationship depth.

    Returns a dict with modifiers that the brain can use to adjust responses.
    """
    metadata = memory.get_metadata()
    depth = metadata.get("relationship_depth", 0.0)
    name = metadata.get("friend_name", "Friend")

    if depth < 0.3:
        return {
            "style": "tentative",
            "use_name_frequency": 0.3,
            "max_sentences": 2,
            "ask_questions": True,
            "reference_history": False,
            "emotional_range": ["good", "bad", "surprised"],
        }
    elif depth < 0.7:
        return {
            "style": "comfortable",
            "use_name_frequency": 0.6,
            "max_sentences": 3,
            "ask_questions": True,
            "reference_history": True,
            "emotional_range": ["good", "bad", "surprised", "happy", "sad", "concerned"],
        }
    else:
        return {
            "style": "deep_bond",
            "use_name_frequency": 0.8,
            "max_sentences": 4,
            "ask_questions": True,
            "reference_history": True,
            "emotional_range": ["good", "bad", "surprised", "happy", "sad", "concerned",
                                "proud", "grateful", "impressed", "frustrated"],
        }
