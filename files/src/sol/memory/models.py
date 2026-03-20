"""Data models for SOL's memory system."""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Fact:
    content: str
    category: str = "general"
    created_at: str = ""
    session_id: Optional[int] = None


@dataclass
class Preference:
    item: str
    sentiment: str = "like"  # "like" or "dislike"
    created_at: str = ""


@dataclass
class MoodEntry:
    mood: str
    intensity: float = 0.5
    trigger: Optional[str] = None
    created_at: str = ""
    session_id: Optional[int] = None


@dataclass
class ConversationSummary:
    session_id: int
    summary: str
    turn_count: int = 0
    mood_trend: str = "neutral"
    key_topics: str = ""
    created_at: str = ""


@dataclass
class JournalEntry:
    content: str
    follow_ups: str = ""
    mood: str = ""
    created_at: str = ""


@dataclass
class Reminder:
    content: str
    trigger_at: str = ""
    recurrence: Optional[str] = None
    completed: bool = False
    created_at: str = ""


@dataclass
class Note:
    content: str
    tags: str = ""
    created_at: str = ""
