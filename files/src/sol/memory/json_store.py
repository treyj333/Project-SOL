"""JSON file-based memory store — backward compatible with sol_memory.json."""

import os
import json
import datetime
from typing import Optional, List, Dict, Any

from sol.memory.base import MemoryStore


class JsonMemoryStore(MemoryStore):
    """Memory backend using a JSON file. Original SOL v1 behavior."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "friend_name": None,
            "facts": [],
            "preferences": [],
            "conversations": 0,
            "first_met": None,
            "last_talked": None,
            "mood_history": [],
            "topics": [],
        }

    def _save(self):
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def get_friend_name(self) -> Optional[str]:
        return self.data.get("friend_name")

    def set_friend_name(self, name: str) -> None:
        self.data["friend_name"] = name
        self._save()

    def get_facts(self, limit: int = 10, category: Optional[str] = None) -> List[str]:
        facts = self.data.get("facts", [])
        return facts[-limit:]

    def add_fact(self, fact: str, category: str = "general") -> None:
        if fact not in self.data["facts"]:
            self.data["facts"].append(fact)
            self._save()

    def get_preferences(self, limit: int = 10) -> List[Dict[str, str]]:
        prefs = []
        for p in self.data.get("preferences", [])[-limit:]:
            if p.startswith("NOT "):
                prefs.append({"item": p[4:], "sentiment": "dislike"})
            else:
                prefs.append({"item": p, "sentiment": "like"})
        return prefs

    def add_preference(self, item: str, sentiment: str = "like") -> None:
        if sentiment == "dislike":
            entry = f"NOT {item}"
        else:
            entry = item
        if entry not in self.data["preferences"]:
            self.data["preferences"].append(entry)
            self._save()

    def get_mood_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.data.get("mood_history", [])[-limit:]

    def add_mood(self, mood: str, intensity: float = 0.5, trigger: Optional[str] = None) -> None:
        entry = {"mood": mood, "time": datetime.datetime.now().isoformat()}
        if trigger:
            entry["trigger"] = trigger
        self.data["mood_history"].append(entry)
        self._save()

    def get_topics(self, limit: int = 10) -> List[str]:
        return self.data.get("topics", [])[-limit:]

    def add_topic(self, topic: str) -> None:
        if topic not in self.data["topics"]:
            self.data["topics"].append(topic)
            if len(self.data["topics"]) > 50:
                self.data["topics"] = self.data["topics"][-50:]
            self._save()

    def get_conversations_count(self) -> int:
        return self.data.get("conversations", 0)

    def increment_conversations(self) -> int:
        self.data["conversations"] = self.data.get("conversations", 0) + 1
        self._save()
        return self.data["conversations"]

    def get_first_met(self) -> Optional[str]:
        return self.data.get("first_met")

    def set_first_met(self, timestamp: str) -> None:
        self.data["first_met"] = timestamp
        self._save()

    def get_last_talked(self) -> Optional[str]:
        return self.data.get("last_talked")

    def set_last_talked(self, timestamp: str) -> None:
        self.data["last_talked"] = timestamp
        self._save()

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "friend_name": self.get_friend_name() or "???",
            "facts_count": len(self.data.get("facts", [])),
            "prefs_count": len(self.data.get("preferences", [])),
            "conversations": self.get_conversations_count(),
            "first_met": self.get_first_met(),
            "last_talked": self.get_last_talked(),
        }

    def supports_feature(self, feature: str) -> bool:
        return False
