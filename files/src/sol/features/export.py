"""Conversation export — save SOL's memory as Markdown or JSON."""

import json
import datetime
from typing import Dict, Any

from sol.memory.base import MemoryStore


def export_markdown(memory: MemoryStore) -> str:
    """Export SOL's memory as a Markdown document."""
    meta = memory.get_metadata()
    lines = []

    lines.append("# SOL Memory Export")
    lines.append(f"*Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")

    # Friend info
    lines.append("## About My Friend")
    lines.append(f"- **Name:** {meta.get('friend_name', 'Unknown')}")
    lines.append(f"- **First met:** {meta.get('first_met', 'Unknown')}")
    lines.append(f"- **Last talked:** {meta.get('last_talked', 'Unknown')}")
    lines.append(f"- **Conversations:** {meta.get('conversations', 0)}")
    lines.append("")

    # Facts
    facts = memory.get_facts(limit=999)
    if facts:
        lines.append("## Things SOL Knows")
        for f in facts:
            lines.append(f"- {f}")
        lines.append("")

    # Preferences
    prefs = memory.get_preferences(limit=999)
    if prefs:
        lines.append("## Likes and Dislikes")
        for p in prefs:
            if p["sentiment"] == "dislike":
                lines.append(f"- Does NOT like: {p['item']}")
            else:
                lines.append(f"- Likes: {p['item']}")
        lines.append("")

    # Topics
    topics = memory.get_topics(limit=50)
    if topics:
        lines.append("## Topics We Discussed")
        lines.append(", ".join(topics))
        lines.append("")

    # Mood history
    moods = memory.get_mood_history(limit=20)
    if moods:
        lines.append("## Mood History")
        for m in moods:
            mood = m.get("mood", "?")
            time_str = m.get("time", "?")
            lines.append(f"- {mood} ({time_str})")
        lines.append("")

    # Conversation summaries
    if memory.supports_feature("summaries"):
        try:
            summaries = memory.get_recent_summaries(limit=20)
            if summaries:
                lines.append("## Conversation Summaries")
                for s in summaries:
                    lines.append(f"- Session {s.get('session_id', '?')}: {s.get('summary', '')}")
                lines.append("")
        except Exception:
            pass

    lines.append("---")
    lines.append("*SOL remember all this. SOL remember more every day.*")

    return "\n".join(lines)


def export_json(memory: MemoryStore) -> str:
    """Export SOL's memory as JSON."""
    data = {
        "export_date": datetime.datetime.now().isoformat(),
        "metadata": memory.get_metadata(),
        "facts": memory.get_facts(limit=999),
        "preferences": memory.get_preferences(limit=999),
        "topics": memory.get_topics(limit=999),
        "mood_history": memory.get_mood_history(limit=999),
    }

    if memory.supports_feature("summaries"):
        try:
            data["conversation_summaries"] = memory.get_recent_summaries(limit=999)
        except Exception:
            pass

    return json.dumps(data, indent=2)


def save_export(memory: MemoryStore, output_path: str, format: str = "markdown"):
    """Export memory to a file.

    Args:
        memory: The memory store to export from.
        output_path: Path to save the export file.
        format: 'markdown' or 'json'.
    """
    if format == "json":
        content = export_json(memory)
    else:
        content = export_markdown(memory)

    with open(output_path, "w") as f:
        f.write(content)
