"""Pattern-matching brain — fallback when no LLM is available."""

import time
import random
import datetime
from typing import List, Dict, Any, Optional

from sol.brain.base import BaseBrain
from sol.brain.personality import (
    GREETINGS, FIRST_MEETING, CONFUSED, GOODBYES,
    HAPPY_RESPONSES, SAD_RESPONSES, JOKES,
    NAME_PATTERNS, FACT_PATTERNS, GOODBYE_WORDS,
    SAD_WORDS, HAPPY_WORDS,
)
from sol.memory.base import MemoryStore


class PatternBrain(BaseBrain):
    """
    SOL's pattern-matching thinking engine. No neural network needed.
    Uses pattern matching, memory lookup, and personality-driven responses.
    The more you talk, the smarter SOL gets about YOU.
    """

    def __init__(self, memory: MemoryStore):
        self.memory = memory
        self.context: List[Dict[str, Any]] = []
        self.session_facts: List[str] = []

    def is_available(self) -> bool:
        return True

    def get_context(self) -> List[Dict[str, Any]]:
        return self.context

    def think(self, user_input: str) -> str:
        """Process input and generate a response."""
        text = user_input.lower().strip()

        if not text:
            return random.choice(CONFUSED)

        self.context.append({"role": "human", "text": text, "time": time.time()})

        # Check for goodbye
        if any(w in text for w in GOODBYE_WORDS):
            self.memory.set_last_talked(datetime.datetime.now().isoformat())
            return random.choice(GOODBYES)

        # Check for name introduction
        if self.memory.get_friend_name() is None:
            name = self._extract_name(text)
            if name:
                self.memory.set_friend_name(name)
                self.memory.set_first_met(datetime.datetime.now().isoformat())
                return f"{name} — got it. Good to meet you. So what's on your mind?"

        # Emotional detection
        if any(w in text for w in SAD_WORDS):
            self.memory.add_mood("sad", trigger=text[:100])
            return random.choice(SAD_RESPONSES)

        if any(w in text for w in HAPPY_WORDS):
            self.memory.add_mood("happy", trigger=text[:100])
            return random.choice(HAPPY_RESPONSES)

        # Learn facts
        fact = self._extract_fact(text)
        if fact:
            existing = self.memory.get_facts(limit=999)
            if fact not in existing:
                self.memory.add_fact(fact)
                name = self.memory.get_friend_name() or "Friend"
                return f"Noted — {fact}. Tell me more about that?"

        # Questions about SOL
        if "who are you" in text or "what are you" in text:
            return "I'm SOL — an AI that lives on your computer. I remember our conversations, I learn about you over time, and I try to actually be useful. Still growing, but I'm getting there."

        if "how are you" in text or "how do you feel" in text:
            ctx_len = len(self.context)
            if ctx_len < 3:
                return "Doing well — just warming up. What's going on with you?"
            else:
                return f"I'm good. We've been talking for a bit now and I feel like I'm getting a better read on things."

        # Recall memory
        if any(w in text for w in ["remember", "do you know", "what do you know", "tell me about me"]):
            return self._recall()

        # Likes
        if "i like" in text or "i love" in text or "my favorite" in text:
            pref = self._extract_preference(text)
            if pref:
                self.memory.add_preference(pref, "like")
                return f"Got it — you're into {pref}. I'll remember that."

        # Dislikes
        if "i don't like" in text or "i hate" in text or "i dislike" in text:
            pref = self._extract_dislike(text)
            if pref:
                self.memory.add_preference(pref, "dislike")
                return f"Understood — not a fan of {pref}. Noted."

        # Time questions
        if "what time" in text or "what day" in text:
            now = datetime.datetime.now()
            return f"It's {now.strftime('%A')}, {now.strftime('%I:%M %p')}."

        # Thank you
        if "thank" in text:
            name = self.memory.get_friend_name() or "Friend"
            return f"Happy to help, {name}. That's what I'm here for."

        # How long known
        if "how long" in text and ("know" in text or "friends" in text or "met" in text):
            first_met = self.memory.get_first_met()
            if first_met:
                first = datetime.datetime.fromisoformat(first_met)
                days = (datetime.datetime.now() - first).days
                if days == 0:
                    return "We just met today! But I'm already learning a lot about you."
                elif days == 1:
                    return "One day in. Still early, but I remember everything from yesterday."
                else:
                    return f"It's been {days} days. I've been keeping track of everything we've talked about."
            return "I'm not sure exactly, but it doesn't matter — we're here now."

        # Jokes
        if "joke" in text or "funny" in text or "laugh" in text:
            return random.choice(JOKES)

        # Topic tracking
        topic = self._extract_topic(text)
        if topic:
            self.memory.add_topic(topic)

        # Context-aware fallback
        return self._contextual_response(text)

    def _extract_name(self, text: str) -> Optional[str]:
        for p in NAME_PATTERNS:
            if p in text:
                rest = text.split(p, 1)[1].strip()
                name = rest.split()[0] if rest.split() else None
                if name:
                    return name.capitalize().rstrip(".,!?")
        return None

    def _extract_fact(self, text: str) -> Optional[str]:
        for p in FACT_PATTERNS:
            if p in text:
                fact = text[text.index(p):]
                fact = fact.strip().rstrip(".,!?")
                if 10 < len(fact) < 200:
                    return fact.capitalize()
        return None

    def _extract_preference(self, text: str) -> Optional[str]:
        for marker in ["i like ", "i love ", "my favorite is ", "my favorite "]:
            if marker in text:
                return text.split(marker, 1)[1].strip().rstrip(".,!?")
        return None

    def _extract_dislike(self, text: str) -> Optional[str]:
        for marker in ["i don't like ", "i hate ", "i dislike "]:
            if marker in text:
                return text.split(marker, 1)[1].strip().rstrip(".,!?")
        return None

    def _extract_topic(self, text: str) -> Optional[str]:
        words = text.split()
        if len(words) >= 2:
            candidates = [w for w in words if len(w) > 4 and w.isalpha()]
            if candidates:
                return max(candidates, key=len)
        return None

    def _recall(self) -> str:
        parts = []
        name = self.memory.get_friend_name()
        if name:
            parts.append(f"Your name is {name}.")
        facts = self.memory.get_facts(limit=5)
        if facts:
            parts.append("Here's what I remember about you:")
            for f in facts:
                parts.append(f"  - {f}")
        prefs = self.memory.get_preferences(limit=5)
        if prefs:
            parts.append("Your likes and dislikes:")
            for p in prefs:
                if p["sentiment"] == "dislike":
                    parts.append(f"  - Not into {p['item']}")
                else:
                    parts.append(f"  - {p['item']}")
        convos = self.memory.get_conversations_count()
        if convos > 0:
            parts.append(f"We've had {convos} conversations so far.")
        if not parts:
            return "I don't know much about you yet. Tell me something — I'll remember it."
        parts.append("I pick up more every time we talk.")
        return "\n".join(parts)

    def _contextual_response(self, text: str) -> str:
        name = self.memory.get_friend_name() or "Friend"
        ctx_size = len(self.context)

        if ctx_size <= 2:
            return random.choice([
                f"I'm listening. Keep going, {name}.",
                "Interesting — tell me more about that.",
                f"Got it. What else is on your mind, {name}?",
            ])

        if ctx_size <= 6:
            return random.choice([
                f"I'm piecing things together from what you've been saying. Go on.",
                f"That connects to something you said earlier. I'm tracking, {name}.",
                f"I hear you. What's the thing that matters most about this?",
                f"Okay, I think I see where you're going with this.",
            ])

        topics = self.memory.get_topics(limit=3)
        topic_mention = f" We've covered {', '.join(topics)} today." if topics else ""
        return random.choice([
            f"Good conversation today.{topic_mention} What else?",
            f"I feel like I'm getting a better picture of how you think.{topic_mention}",
            f"We've covered a lot of ground, {name}.{topic_mention} Anything else?",
            f"I'm learning a lot from this conversation. Keep going.",
        ])
