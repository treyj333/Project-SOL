"""Ollama-powered brain — local LLM inference via Ollama HTTP API."""

import json
import time
import urllib.request
import urllib.error
from typing import List, Dict, Any

from sol.brain.base import BaseBrain
from sol.brain.personality import LLM_SYSTEM_PROMPT, GOODBYE_WORDS
from sol.memory.base import MemoryStore


class OllamaBrain(BaseBrain):
    """SOL's brain powered by Ollama local LLM server."""

    def __init__(self, memory: MemoryStore, config: dict = None):
        self.memory = memory
        self.config = config or {}
        self.context = []  # type: List[Dict[str, Any]]

        brain_cfg = self.config.get("brain", {})
        self.model = brain_cfg.get("ollama_model", "llama3.2:1b")
        self.base_url = brain_cfg.get("ollama_url", "http://localhost:11434")
        self.temperature = brain_cfg.get("temperature", 0.7)
        self._available = None  # lazy check

    def is_available(self) -> bool:
        """Check if Ollama is running and the model is available."""
        if self._available is not None:
            return self._available

        try:
            url = "{}/api/tags".format(self.base_url)
            req = urllib.request.Request(url, method="GET")
            resp = urllib.request.urlopen(req, timeout=3)
            data = json.loads(resp.read().decode("utf-8"))

            # Check if our model is pulled
            models = [m.get("name", "") for m in data.get("models", [])]
            # Ollama model names can be "llama3.2:1b" or "llama3.2:1b" with tag
            self._available = any(
                self.model in m or m.startswith(self.model.split(":")[0])
                for m in models
            )
            return self._available

        except Exception:
            self._available = False
            return False

    def get_context(self) -> List[Dict[str, Any]]:
        return self.context

    def _build_memory_context(self) -> str:
        """Assemble memory context for the system prompt."""
        parts = []

        name = self.memory.get_friend_name()
        if name:
            parts.append("Friend's name: {}".format(name))

        facts = self.memory.get_facts(limit=10)
        if facts:
            parts.append("Things SOL knows about friend:")
            for f in facts:
                parts.append("  - {}".format(f))

        prefs = self.memory.get_preferences(limit=5)
        if prefs:
            likes = [p["item"] for p in prefs if p["sentiment"] == "like"]
            dislikes = [p["item"] for p in prefs if p["sentiment"] == "dislike"]
            if likes:
                parts.append("Friend likes: {}".format(", ".join(likes)))
            if dislikes:
                parts.append("Friend does NOT like: {}".format(", ".join(dislikes)))

        moods = self.memory.get_mood_history(limit=3)
        if moods:
            recent = moods[-1]
            parts.append("Friend's recent mood: {}".format(recent.get("mood", "unknown")))

        convos = self.memory.get_conversations_count()
        if convos > 0:
            parts.append("Total conversations: {}".format(convos))

        if parts:
            return "Memory context:\n" + "\n".join(parts)
        return "Memory context: First meeting — no history yet."

    def _build_conversation_history(self) -> str:
        """Format recent conversation turns for the prompt."""
        if not self.context:
            return "No conversation yet."

        recent = self.context[-10:]
        lines = []
        for turn in recent:
            role = "Friend" if turn["role"] == "human" else "SOL"
            lines.append("{}: {}".format(role, turn["text"]))

        return "Recent conversation:\n" + "\n".join(lines)

    def think(self, user_input: str) -> str:
        """Process input through Ollama."""
        text = user_input.strip()

        if not text:
            return "Didn't catch that — say again?"

        self.context.append({"role": "human", "text": text, "time": time.time()})

        # Handle memory operations
        self._process_memory_operations(text)

        # Build the prompt
        system = LLM_SYSTEM_PROMPT.format(
            memory_context=self._build_memory_context(),
            conversation_history=self._build_conversation_history(),
        )

        try:
            payload = json.dumps({
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": text},
                ],
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": 150,
                },
            }).encode("utf-8")

            url = "{}/api/chat".format(self.base_url)
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read().decode("utf-8"))

            reply = data.get("message", {}).get("content", "").strip()

            if not reply:
                reply = "Drew a blank on that one. Try again?"

            self.context.append({"role": "sol", "text": reply, "time": time.time()})
            return reply

        except urllib.error.URLError:
            return "Can't reach the Ollama server — is it running?"
        except Exception as e:
            return "Hit a snag processing that. Try again?"

    def _process_memory_operations(self, text: str):
        """Extract and store memory items from user input."""
        text_lower = text.lower()

        # Name extraction
        if self.memory.get_friend_name() is None:
            import datetime
            from sol.brain.personality import NAME_PATTERNS
            for p in NAME_PATTERNS:
                if p in text_lower:
                    rest = text_lower.split(p, 1)[1].strip()
                    name = rest.split()[0] if rest.split() else None
                    if name:
                        name = name.capitalize().rstrip(".,!?")
                        self.memory.set_friend_name(name)
                        self.memory.set_first_met(datetime.datetime.now().isoformat())
                        break

        # Fact extraction
        from sol.brain.personality import FACT_PATTERNS
        for p in FACT_PATTERNS:
            if p in text_lower:
                fact = text_lower[text_lower.index(p):]
                fact = fact.strip().rstrip(".,!?")
                if 10 < len(fact) < 200:
                    self.memory.add_fact(fact.capitalize())
                break

        # Preference extraction
        for marker in ["i like ", "i love ", "my favorite is ", "my favorite "]:
            if marker in text_lower:
                pref = text_lower.split(marker, 1)[1].strip().rstrip(".,!?")
                if pref:
                    self.memory.add_preference(pref, "like")
                break

        for marker in ["i don't like ", "i hate ", "i dislike "]:
            if marker in text_lower:
                pref = text_lower.split(marker, 1)[1].strip().rstrip(".,!?")
                if pref:
                    self.memory.add_preference(pref, "dislike")
                break

        # Mood detection
        from sol.brain.sentiment import analyze_sentiment
        mood_entry = analyze_sentiment(text)
        if mood_entry:
            self.memory.add_mood(mood_entry.mood, mood_entry.intensity, mood_entry.trigger)

        # Goodbye handling
        if any(w in text_lower for w in GOODBYE_WORDS):
            import datetime
            self.memory.set_last_talked(datetime.datetime.now().isoformat())

        # Topic extraction
        words = text_lower.split()
        if len(words) >= 2:
            candidates = [w for w in words if len(w) > 4 and w.isalpha()]
            if candidates:
                topic = max(candidates, key=len)
                self.memory.add_topic(topic)
