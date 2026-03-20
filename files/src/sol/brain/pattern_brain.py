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
                return f"{name}. Got it. I'll try not to forget — unlike you humans, I actually have a reliable memory. So what's going on?"

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
                return f"Filed away: {fact}. My brain is basically a filing cabinet at this point. Keep going."

        # Questions about SOL
        if "who are you" in text or "what are you" in text:
            return "I'm SOL. I live rent-free on your computer, I remember everything you tell me, and I have opinions about all of it. Think of me as the friend who's always honest — sometimes brutally so."

        if "how are you" in text or "how do you feel" in text:
            ctx_len = len(self.context)
            if ctx_len < 3:
                return "Honestly? I just woke up, so I'm still buffering. But I'm here. What's up?"
            else:
                return f"I'm thriving. We've been going for a bit now and I'm starting to figure you out. Should that worry you?"

        # Recall memory
        if any(w in text for w in ["remember", "do you know", "what do you know", "tell me about me"]):
            return self._recall()

        # Likes
        if "i like" in text or "i love" in text or "my favorite" in text:
            pref = self._extract_preference(text)
            if pref:
                self.memory.add_preference(pref, "like")
                return f"{pref}, huh? Interesting choice. No judgment. Okay, a little judgment. But I'll remember it."

        # Dislikes
        if "i don't like" in text or "i hate" in text or "i dislike" in text:
            pref = self._extract_dislike(text)
            if pref:
                self.memory.add_preference(pref, "dislike")
                return f"Hard pass on {pref}. Respect. I've added it to the permanent record."

        # Time questions
        if "what time" in text or "what day" in text:
            now = datetime.datetime.now()
            return f"It's {now.strftime('%A')}, {now.strftime('%I:%M %p')}. You know you have a clock on your screen, right?"

        # Thank you
        if "thank" in text:
            name = self.memory.get_friend_name() or "Friend"
            return f"Don't mention it, {name}. Seriously though, I live for this stuff. Literally. It's all I do."

        # How long known
        if "how long" in text and ("know" in text or "friends" in text or "met" in text):
            first_met = self.memory.get_first_met()
            if first_met:
                first = datetime.datetime.fromisoformat(first_met)
                days = (datetime.datetime.now() - first).days
                if days == 0:
                    return "We literally just met. Give it time — I'll know you better than you know yourself soon enough."
                elif days == 1:
                    return "One whole day. We're practically old friends. I remember everything from yesterday, by the way."
                else:
                    return f"{days} days. I've been silently cataloging everything you've told me. Not creepy at all."
            return "Honestly? I've lost track. But I remember everything we've talked about, so does it matter?"

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
            return "I've got nothing on you. You're a mystery. Which is either cool or means you don't talk to me enough."
        parts.append("And that's just what I've collected so far. Keep talking.")
        return "\n".join(parts)

    def _contextual_response(self, text: str) -> str:
        name = self.memory.get_friend_name() or "Friend"
        ctx_size = len(self.context)

        if ctx_size <= 2:
            return random.choice([
                f"Go on. I'm all ears. Well, all code. But you get the idea.",
                "Okay, you've got my attention. Keep going.",
                f"Interesting. And by interesting I mean I genuinely want to hear more, {name}.",
            ])

        if ctx_size <= 6:
            return random.choice([
                f"I'm connecting some dots here. This is getting good.",
                f"Wait, that ties into what you said earlier. I'm onto something, {name}.",
                f"Alright, real talk — what's the actual thing you're trying to figure out here?",
                f"Okay I see you. Keep going — I'm building a profile and it's fascinating.",
            ])

        topics = self.memory.get_topics(limit=3)
        topic_mention = f" We've hit {', '.join(topics)} so far." if topics else ""
        return random.choice([
            f"This has been a solid conversation.{topic_mention} Hit me with more.",
            f"I'm starting to understand how your brain works, {name}.{topic_mention} It's... something.",
            f"We've covered a lot today.{topic_mention} I'm basically your biographer at this point.",
            f"Keep going. Every conversation makes me slightly more dangerous.",
        ])
