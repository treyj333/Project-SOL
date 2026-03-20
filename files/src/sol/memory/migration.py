"""Migration from sol_memory.json to SQLite — one-time, automatic."""

import os
import json
import shutil

from sol.memory.sqlite_store import SqliteMemoryStore


def maybe_migrate(json_path: str, db_path: str) -> bool:
    """Auto-migrate from JSON to SQLite if needed.

    Triggered when:
    - sol_memory.json exists AND
    - sol_memory.db does NOT exist

    Returns True if migration happened, False otherwise.
    """
    if not os.path.exists(json_path):
        return False

    if os.path.exists(db_path):
        return False

    try:
        return _do_migrate(json_path, db_path)
    except Exception:
        # Migration failed — clean up partial DB and leave JSON intact
        if os.path.exists(db_path):
            os.remove(db_path)
        return False


def _do_migrate(json_path: str, db_path: str) -> bool:
    """Perform the actual migration."""
    with open(json_path, "r") as f:
        data = json.load(f)

    store = SqliteMemoryStore(db_path)

    # Migrate friend name
    name = data.get("friend_name")
    if name:
        store.set_friend_name(name)

    # Migrate timestamps
    first_met = data.get("first_met")
    if first_met:
        store.set_first_met(first_met)

    last_talked = data.get("last_talked")
    if last_talked:
        store.set_last_talked(last_talked)

    # Migrate conversation count
    convos = data.get("conversations", 0)
    if convos > 0:
        store._set_meta("conversations_count", str(convos))

    # Migrate facts
    for fact in data.get("facts", []):
        store.add_fact(fact, category="general")

    # Migrate preferences (parse "NOT x" as dislike)
    for pref in data.get("preferences", []):
        if pref.startswith("NOT "):
            store.add_preference(pref[4:], "dislike")
        else:
            store.add_preference(pref, "like")

    # Migrate mood history
    for mood_entry in data.get("mood_history", []):
        mood = mood_entry.get("mood", "neutral")
        store.add_mood(mood)

    # Migrate topics
    for topic in data.get("topics", []):
        store.add_topic(topic)

    store.close()

    # Create backup of original JSON
    backup_path = json_path + ".backup"
    shutil.copy2(json_path, backup_path)

    return True
