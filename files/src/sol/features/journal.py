"""Journal mode — guided daily reflection with follow-up questions."""

import json
from typing import List, Dict, Any, Optional

from sol.memory.base import MemoryStore

# Template follow-up questions for pattern brain mode
JOURNAL_QUESTIONS = [
    "What was the best part of your day?",
    "Was there anything that made you feel bad today?",
    "Did you learn something new today?",
    "Is there anything you want to do differently tomorrow?",
    "How do you feel right now, in this moment?",
]

JOURNAL_TRIGGERS = [
    "let's journal", "lets journal", "journal time",
    "tell you about my day", "about my day",
    "write in my journal", "diary",
]


def is_journal_trigger(text: str) -> bool:
    """Check if user input triggers journal mode."""
    text_lower = text.lower().strip()
    return any(trigger in text_lower for trigger in JOURNAL_TRIGGERS)


def get_journal_prompt(question_index: int) -> Optional[str]:
    """Get the next journal follow-up question."""
    if question_index < len(JOURNAL_QUESTIONS):
        question = JOURNAL_QUESTIONS[question_index]
        return f"SOL want to know: {question}"
    return None


def save_journal_entry(memory: MemoryStore, content: str, follow_ups: List[Dict[str, str]] = None, mood: str = ""):
    """Save a journal entry if the memory backend supports it."""
    if memory.supports_feature("journal"):
        follow_ups_json = json.dumps(follow_ups) if follow_ups else ""
        memory.add_journal_entry(content, follow_ups_json, mood)


def generate_session_summary(context: List[Dict[str, Any]], memory: MemoryStore):
    """Generate and save a session summary after the conversation ends."""
    if not memory.supports_feature("summaries"):
        return

    if not context:
        return

    turn_count = len(context)
    human_turns = [t for t in context if t.get("role") == "human"]

    # Extract topics from conversation
    all_words = " ".join(t.get("text", "") for t in human_turns)
    words = all_words.split()
    topic_candidates = [w for w in words if len(w) > 4 and w.isalpha()]
    # Get top 3 most common long words as topics
    topic_freq = {}
    for w in topic_candidates:
        topic_freq[w] = topic_freq.get(w, 0) + 1
    top_topics = sorted(topic_freq.items(), key=lambda x: x[1], reverse=True)[:3]
    key_topics = ", ".join(t[0] for t in top_topics) if top_topics else "general chat"

    # Simple mood trend
    mood_trend = "neutral"
    moods = memory.get_mood_history(limit=5)
    if moods:
        recent_moods = [m.get("mood", "neutral") for m in moods[-3:]]
        if "sad" in recent_moods or "anxious" in recent_moods:
            mood_trend = "negative"
        elif "happy" in recent_moods or "excited" in recent_moods:
            mood_trend = "positive"

    summary = (
        f"Conversation with {turn_count} exchanges. "
        f"Topics: {key_topics}. "
        f"Mood: {mood_trend}."
    )

    session_id = memory.get_conversations_count()
    memory.add_conversation_summary(session_id, summary, turn_count, mood_trend, key_topics)
