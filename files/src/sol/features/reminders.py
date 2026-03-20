"""Reminders system — time-based triggers with natural language parsing."""

import re
import datetime
from typing import List, Optional

from sol.memory.base import MemoryStore

REMINDER_TRIGGERS = [
    "remind me to ", "remind me about ", "don't let me forget ",
    "dont let me forget ", "reminder to ", "reminder about ",
    "remember to tell me ", "set a reminder ",
]

# Relative time patterns
TIME_PATTERNS = {
    r"in (\d+) minute": lambda m: datetime.timedelta(minutes=int(m)),
    r"in (\d+) hour": lambda m: datetime.timedelta(hours=int(m)),
    r"in (\d+) day": lambda m: datetime.timedelta(days=int(m)),
    r"in (\d+) week": lambda m: datetime.timedelta(weeks=int(m)),
    r"tomorrow": lambda m: datetime.timedelta(days=1),
    r"next week": lambda m: datetime.timedelta(weeks=1),
    r"next month": lambda m: datetime.timedelta(days=30),
    r"tonight": lambda m: datetime.timedelta(hours=6),
    r"this evening": lambda m: datetime.timedelta(hours=4),
}


def is_reminder_trigger(text: str) -> bool:
    """Check if user input is a reminder request."""
    text_lower = text.lower().strip()
    return any(trigger in text_lower for trigger in REMINDER_TRIGGERS)


def parse_reminder(text: str) -> Optional[dict]:
    """Parse a reminder from natural language.

    Returns dict with 'content' and 'trigger_at' keys, or None.
    """
    text_lower = text.lower().strip()

    # Extract the reminder content
    content = text_lower
    matched = False
    for trigger in REMINDER_TRIGGERS:
        if trigger.strip() in content:
            parts = content.split(trigger.strip(), 1)
            content = parts[1].strip() if len(parts) > 1 else ""
            matched = True
            break

    if not content:
        return None

    # Try to extract a time
    trigger_time = None
    for pattern, delta_fn in TIME_PATTERNS.items():
        match = re.search(pattern, text_lower)
        if match:
            groups = match.groups()
            delta = delta_fn(groups[0] if groups else None)
            trigger_time = datetime.datetime.now() + delta
            # Remove time part from content
            content = re.sub(pattern + r"s?", "", content).strip()
            break

    # Default: remind in 1 hour if no time specified
    if trigger_time is None:
        trigger_time = datetime.datetime.now() + datetime.timedelta(hours=1)

    # Clean up content
    content = content.strip().rstrip(".,!?")
    if not content:
        return None

    return {
        "content": content,
        "trigger_at": trigger_time.isoformat(),
    }


def check_pending(memory: MemoryStore) -> List[str]:
    """Check for pending reminders. Returns list of reminder content strings."""
    if not memory.supports_feature("reminders"):
        return []

    try:
        pending = memory.get_pending_reminders()
        results = []
        for r in pending:
            results.append(r["content"])
            memory.complete_reminder(r["id"])
        return results
    except Exception:
        return []


def save_reminder(memory: MemoryStore, content: str, trigger_at: str, recurrence: str = None):
    """Save a reminder if the memory backend supports it."""
    if memory.supports_feature("reminders"):
        memory.add_reminder(content, trigger_at, recurrence)
