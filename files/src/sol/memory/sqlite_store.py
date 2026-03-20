"""SQLite-based memory store — rich, searchable, persistent."""

import os
import sqlite3
import datetime
from typing import Optional, List, Dict, Any

from sol.memory.base import MemoryStore

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS metadata (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS facts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    category   TEXT NOT NULL DEFAULT 'general',
    content    TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    session_id INTEGER
);

CREATE TABLE IF NOT EXISTS preferences (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    item       TEXT NOT NULL,
    sentiment  TEXT NOT NULL DEFAULT 'like',
    created_at TEXT NOT NULL,
    UNIQUE(item, sentiment)
);

CREATE TABLE IF NOT EXISTS moods (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    mood       TEXT NOT NULL,
    intensity  REAL DEFAULT 0.5,
    trigger_text TEXT,
    created_at TEXT NOT NULL,
    session_id INTEGER
);

CREATE TABLE IF NOT EXISTS topics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    topic           TEXT NOT NULL UNIQUE,
    mention_count   INTEGER DEFAULT 1,
    first_mentioned TEXT NOT NULL,
    last_mentioned  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversation_summaries (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    summary    TEXT NOT NULL,
    turn_count INTEGER,
    mood_trend TEXT,
    key_topics TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    content    TEXT NOT NULL,
    follow_ups TEXT,
    mood       TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reminders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    content     TEXT NOT NULL,
    trigger_at  TEXT NOT NULL,
    recurrence  TEXT,
    completed   INTEGER DEFAULT 0,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    content    TEXT NOT NULL,
    tags       TEXT,
    created_at TEXT NOT NULL
);
"""

FTS_SQL = """
CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(content, content=facts, content_rowid=id);
CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(content, content=notes, content_rowid=id);
"""

TRIGGERS_SQL = """
CREATE TRIGGER IF NOT EXISTS facts_ai AFTER INSERT ON facts BEGIN
    INSERT INTO facts_fts(rowid, content) VALUES (new.id, new.content);
END;

CREATE TRIGGER IF NOT EXISTS facts_ad AFTER DELETE ON facts BEGIN
    INSERT INTO facts_fts(facts_fts, rowid, content) VALUES('delete', old.id, old.content);
END;

CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
    INSERT INTO notes_fts(rowid, content) VALUES (new.id, new.content);
END;

CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
    INSERT INTO notes_fts(notes_fts, rowid, content) VALUES('delete', old.id, old.content);
END;
"""


class SqliteMemoryStore(MemoryStore):
    """Memory backend using SQLite — rich queries, FTS, categories."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self):
        cursor = self.conn.cursor()
        cursor.executescript(SCHEMA_SQL)
        try:
            cursor.executescript(FTS_SQL)
            cursor.executescript(TRIGGERS_SQL)
        except Exception:
            pass  # FTS may not be available on all SQLite builds
        self.conn.commit()

    def _now(self) -> str:
        return datetime.datetime.now().isoformat()

    def _get_meta(self, key: str) -> Optional[str]:
        row = self.conn.execute("SELECT value FROM metadata WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def _set_meta(self, key: str, value: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            (key, value),
        )
        self.conn.commit()

    # ── Friend name ──

    def get_friend_name(self) -> Optional[str]:
        return self._get_meta("friend_name")

    def set_friend_name(self, name: str) -> None:
        self._set_meta("friend_name", name)

    # ── Facts ──

    def get_facts(self, limit: int = 10, category: Optional[str] = None) -> List[str]:
        if category:
            rows = self.conn.execute(
                "SELECT content FROM facts WHERE category = ? ORDER BY id DESC LIMIT ?",
                (category, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT content FROM facts ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [r["content"] for r in reversed(rows)]

    def add_fact(self, fact: str, category: str = "general") -> None:
        try:
            self.conn.execute(
                "INSERT INTO facts (category, content, created_at) VALUES (?, ?, ?)",
                (category, fact, self._now()),
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # duplicate

    # ── Preferences ──

    def get_preferences(self, limit: int = 10) -> List[Dict[str, str]]:
        rows = self.conn.execute(
            "SELECT item, sentiment FROM preferences ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [{"item": r["item"], "sentiment": r["sentiment"]} for r in reversed(rows)]

    def add_preference(self, item: str, sentiment: str = "like") -> None:
        try:
            self.conn.execute(
                "INSERT INTO preferences (item, sentiment, created_at) VALUES (?, ?, ?)",
                (item, sentiment, self._now()),
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    # ── Moods ──

    def get_mood_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT mood, intensity, trigger_text, created_at FROM moods ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            {"mood": r["mood"], "intensity": r["intensity"],
             "trigger": r["trigger_text"], "time": r["created_at"]}
            for r in reversed(rows)
        ]

    def add_mood(self, mood: str, intensity: float = 0.5, trigger: Optional[str] = None) -> None:
        self.conn.execute(
            "INSERT INTO moods (mood, intensity, trigger_text, created_at) VALUES (?, ?, ?, ?)",
            (mood, intensity, trigger, self._now()),
        )
        self.conn.commit()

    def get_last_mood(self) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT mood, intensity, trigger_text, created_at FROM moods ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if row:
            return {"mood": row["mood"], "intensity": row["intensity"],
                    "trigger": row["trigger_text"], "time": row["created_at"]}
        return None

    # ── Topics ──

    def get_topics(self, limit: int = 10) -> List[str]:
        rows = self.conn.execute(
            "SELECT topic FROM topics ORDER BY last_mentioned DESC LIMIT ?", (limit,)
        ).fetchall()
        return [r["topic"] for r in reversed(rows)]

    def add_topic(self, topic: str) -> None:
        now = self._now()
        existing = self.conn.execute("SELECT id FROM topics WHERE topic = ?", (topic,)).fetchone()
        if existing:
            self.conn.execute(
                "UPDATE topics SET mention_count = mention_count + 1, last_mentioned = ? WHERE topic = ?",
                (now, topic),
            )
        else:
            self.conn.execute(
                "INSERT INTO topics (topic, first_mentioned, last_mentioned) VALUES (?, ?, ?)",
                (topic, now, now),
            )
        self.conn.commit()

    # ── Conversations ──

    def get_conversations_count(self) -> int:
        val = self._get_meta("conversations_count")
        return int(val) if val else 0

    def increment_conversations(self) -> int:
        count = self.get_conversations_count() + 1
        self._set_meta("conversations_count", str(count))
        return count

    # ── Timestamps ──

    def get_first_met(self) -> Optional[str]:
        return self._get_meta("first_met")

    def set_first_met(self, timestamp: str) -> None:
        self._set_meta("first_met", timestamp)

    def get_last_talked(self) -> Optional[str]:
        return self._get_meta("last_talked")

    def set_last_talked(self, timestamp: str) -> None:
        self._set_meta("last_talked", timestamp)

    # ── Metadata for display ──

    def get_metadata(self) -> Dict[str, Any]:
        facts_count = self.conn.execute("SELECT COUNT(*) as c FROM facts").fetchone()["c"]
        prefs_count = self.conn.execute("SELECT COUNT(*) as c FROM preferences").fetchone()["c"]
        last_mood = self.get_last_mood()

        return {
            "friend_name": self.get_friend_name() or "???",
            "facts_count": facts_count,
            "prefs_count": prefs_count,
            "conversations": self.get_conversations_count(),
            "first_met": self.get_first_met(),
            "last_talked": self.get_last_talked(),
            "current_mood": last_mood["mood"] if last_mood else None,
            "relationship_depth": self._compute_relationship_depth(facts_count, prefs_count),
        }

    def _compute_relationship_depth(self, facts_count: int = None, prefs_count: int = None) -> float:
        if facts_count is None:
            facts_count = self.conn.execute("SELECT COUNT(*) as c FROM facts").fetchone()["c"]
        convos = self.get_conversations_count()
        first_met = self.get_first_met()
        mood_count = self.conn.execute("SELECT COUNT(*) as c FROM moods").fetchone()["c"]

        days_known = 0
        if first_met:
            try:
                delta = datetime.datetime.now() - datetime.datetime.fromisoformat(first_met)
                days_known = delta.days
            except Exception:
                pass

        score = (
            min(facts_count / 50, 1.0) * 0.3
            + min(convos / 100, 1.0) * 0.3
            + min(days_known / 365, 1.0) * 0.2
            + min(mood_count / 50, 1.0) * 0.2
        )
        return round(score, 3)

    # ── Conversation summaries ──

    def add_conversation_summary(self, session_id: int, summary: str,
                                  turn_count: int = 0, mood_trend: str = "neutral",
                                  key_topics: str = "") -> None:
        self.conn.execute(
            "INSERT INTO conversation_summaries (session_id, summary, turn_count, mood_trend, key_topics, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, summary, turn_count, mood_trend, key_topics, self._now()),
        )
        self.conn.commit()

    def get_recent_summaries(self, limit: int = 5) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM conversation_summaries ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in reversed(rows)]

    # ── Journal ──

    def add_journal_entry(self, content: str, follow_ups: str = "", mood: str = "") -> None:
        self.conn.execute(
            "INSERT INTO journal_entries (content, follow_ups, mood, created_at) VALUES (?, ?, ?, ?)",
            (content, follow_ups, mood, self._now()),
        )
        self.conn.commit()

    def get_journal_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM journal_entries ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in reversed(rows)]

    # ── Reminders ──

    def add_reminder(self, content: str, trigger_at: str, recurrence: str = None) -> None:
        self.conn.execute(
            "INSERT INTO reminders (content, trigger_at, recurrence, created_at) VALUES (?, ?, ?, ?)",
            (content, trigger_at, recurrence, self._now()),
        )
        self.conn.commit()

    def get_pending_reminders(self) -> List[Dict[str, Any]]:
        now = self._now()
        rows = self.conn.execute(
            "SELECT * FROM reminders WHERE completed = 0 AND trigger_at <= ? ORDER BY trigger_at",
            (now,),
        ).fetchall()
        return [dict(r) for r in rows]

    def complete_reminder(self, reminder_id: int) -> None:
        self.conn.execute("UPDATE reminders SET completed = 1 WHERE id = ?", (reminder_id,))
        self.conn.commit()

    # ── Notes ──

    def add_note(self, content: str, tags: str = "") -> None:
        self.conn.execute(
            "INSERT INTO notes (content, tags, created_at) VALUES (?, ?, ?)",
            (content, tags, self._now()),
        )
        self.conn.commit()

    def search_notes(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            rows = self.conn.execute(
                "SELECT n.* FROM notes n JOIN notes_fts f ON n.id = f.rowid "
                "WHERE notes_fts MATCH ? LIMIT ?",
                (query, limit),
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            # FTS not available, fall back to LIKE
            rows = self.conn.execute(
                "SELECT * FROM notes WHERE content LIKE ? LIMIT ?",
                (f"%{query}%", limit),
            ).fetchall()
            return [dict(r) for r in rows]

    def search_facts(self, query: str, limit: int = 5) -> List[str]:
        try:
            rows = self.conn.execute(
                "SELECT f.content FROM facts f JOIN facts_fts ff ON f.id = ff.rowid "
                "WHERE facts_fts MATCH ? LIMIT ?",
                (query, limit),
            ).fetchall()
            return [r["content"] for r in rows]
        except Exception:
            rows = self.conn.execute(
                "SELECT content FROM facts WHERE content LIKE ? LIMIT ?",
                (f"%{query}%", limit),
            ).fetchall()
            return [r["content"] for r in rows]

    # ── Feature support ──

    def supports_feature(self, feature: str) -> bool:
        return feature in ("journal", "reminders", "notes", "summaries", "search")

    def close(self):
        self.conn.close()
