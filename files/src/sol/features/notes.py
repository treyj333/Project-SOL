"""Quick notes — save and recall short pieces of information."""

from typing import List, Optional

from sol.memory.base import MemoryStore

NOTE_TRIGGERS = [
    "remember that ", "note that ", "save this ",
    "write down ", "keep in mind ", "don't forget that ",
    "dont forget that ", "make a note ",
]

RECALL_TRIGGERS = [
    "what did i tell you about ", "what do you know about ",
    "find my note about ", "search notes for ",
    "do you remember when i said ",
]


def is_note_trigger(text: str) -> bool:
    """Check if user input is a note-saving request."""
    text_lower = text.lower().strip()
    return any(trigger in text_lower for trigger in NOTE_TRIGGERS)


def is_recall_trigger(text: str) -> bool:
    """Check if user is trying to recall a note."""
    text_lower = text.lower().strip()
    return any(trigger in text_lower for trigger in RECALL_TRIGGERS)


def extract_note(text: str) -> Optional[str]:
    """Extract the note content from user input."""
    text_lower = text.lower().strip()

    for trigger in NOTE_TRIGGERS:
        if trigger in text_lower:
            content = text_lower.split(trigger, 1)[1].strip().rstrip(".,!?")
            if content:
                return content
    return None


def extract_recall_query(text: str) -> Optional[str]:
    """Extract the search query for note recall."""
    text_lower = text.lower().strip()

    for trigger in RECALL_TRIGGERS:
        if trigger in text_lower:
            query = text_lower.split(trigger, 1)[1].strip().rstrip(".,!?")
            if query:
                return query
    return None


def save_note(memory: MemoryStore, content: str, tags: str = ""):
    """Save a note if the memory backend supports it."""
    if memory.supports_feature("notes"):
        memory.add_note(content, tags)


def search_notes(memory: MemoryStore, query: str, limit: int = 5) -> List[str]:
    """Search notes by query. Returns list of matching note contents."""
    if not memory.supports_feature("notes"):
        return []

    try:
        results = memory.search_notes(query, limit)
        return [r["content"] for r in results]
    except Exception:
        return []
