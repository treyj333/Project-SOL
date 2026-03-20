"""LLM-powered brain — local inference via llama-cpp-python."""

import time
from typing import List, Dict, Any, Optional

from sol.brain.base import BaseBrain
from sol.brain.personality import LLM_SYSTEM_PROMPT, GOODBYE_WORDS
from sol.memory.base import MemoryStore


class LLMBrain(BaseBrain):
    """SOL's brain powered by a local LLM via llama-cpp-python."""

    def __init__(self, model_path: str, memory: MemoryStore, config: dict = None):
        self.memory = memory
        self.config = config or {}
        self.context: List[Dict[str, Any]] = []
        self.model = None
        self._available = False

        try:
            from llama_cpp import Llama

            n_ctx = self.config.get("brain", {}).get("llm_context_length", 2048)
            n_threads = self.config.get("brain", {}).get("llm_threads", 4)
            temperature = self.config.get("brain", {}).get("temperature", 0.7)

            self.model = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=False,
            )
            self.temperature = temperature
            self._available = True
        except Exception:
            pass

    def is_available(self) -> bool:
        return self._available

    def get_context(self) -> List[Dict[str, Any]]:
        return self.context

    def _build_memory_context(self) -> str:
        """Assemble memory context for the system prompt."""
        parts = []

        name = self.memory.get_friend_name()
        if name:
            parts.append(f"Friend's name: {name}")

        facts = self.memory.get_facts(limit=10)
        if facts:
            parts.append("Things SOL knows about friend:")
            for f in facts:
                parts.append(f"  - {f}")

        prefs = self.memory.get_preferences(limit=5)
        if prefs:
            likes = [p["item"] for p in prefs if p["sentiment"] == "like"]
            dislikes = [p["item"] for p in prefs if p["sentiment"] == "dislike"]
            if likes:
                parts.append(f"Friend likes: {', '.join(likes)}")
            if dislikes:
                parts.append(f"Friend does NOT like: {', '.join(dislikes)}")

        moods = self.memory.get_mood_history(limit=3)
        if moods:
            recent = moods[-1]
            parts.append(f"Friend's recent mood: {recent.get('mood', 'unknown')}")

        convos = self.memory.get_conversations_count()
        if convos > 0:
            parts.append(f"Total conversations: {convos}")

        if parts:
            return "Memory context:\n" + "\n".join(parts)
        return "Memory context: SOL not know friend yet. First meeting."

    def _build_conversation_history(self) -> str:
        """Format recent conversation turns for the prompt."""
        if not self.context:
            return "No conversation yet."

        # Use last 10 turns to stay within token budget
        recent = self.context[-10:]
        lines = []
        for turn in recent:
            role = "Friend" if turn["role"] == "human" else "SOL"
            lines.append(f"{role}: {turn['text']}")

        return "Recent conversation:\n" + "\n".join(lines)

    def think(self, user_input: str) -> str:
        """Process input through the local LLM."""
        text = user_input.strip()

        if not text:
            return "SOL not hear anything. Say again?"

        self.context.append({"role": "human", "text": text, "time": time.time()})

        # Handle memory operations that need direct access
        self._process_memory_operations(text)

        # Build the prompt
        system = LLM_SYSTEM_PROMPT.format(
            memory_context=self._build_memory_context(),
            conversation_history=self._build_conversation_history(),
        )

        try:
            response = self.model.create_chat_completion(
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": text},
                ],
                max_tokens=150,
                temperature=self.temperature,
                stop=["Friend:", "\n\n"],
            )

            reply = response["choices"][0]["message"]["content"].strip()

            # Store SOL's response in context
            self.context.append({"role": "sol", "text": reply, "time": time.time()})

            return reply

        except Exception as e:
            return f"SOL brain hurt. Error. SOL try again? ({e})"

    def _process_memory_operations(self, text: str):
        """Extract and store memory items from user input."""
        text_lower = text.lower()

        # Name extraction (first meeting)
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
