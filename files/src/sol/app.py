"""SOL Application Orchestrator — wires all components together."""

import os
import sys
import time
import random
import datetime

from sol import __version__
from sol.config import load_config, get, resolve_path
from sol.brain.base import BaseBrain
from sol.brain.pattern_brain import PatternBrain
from sol.brain.personality import FIRST_MEETING, GOODBYE_WORDS
from sol.memory.base import MemoryStore
from sol.memory.json_store import JsonMemoryStore
from sol.ui.cli import CliUI
from sol.ui.base import UIBase


class SolApp:
    """Main application — detects available components and runs SOL."""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            # Default to the directory containing the original sol.py
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.base_dir = base_dir
        self.config = load_config(base_dir)
        self.ui: UIBase = self._init_ui()
        self.memory: MemoryStore = self._init_memory()
        self.brain_name = "pattern matching"
        self.brain: BaseBrain = self._init_brain()
        self.voice_in = self._init_voice_input()
        self.voice_out = self._init_voice_output()
        self.plugins = self._init_plugins()

    def _init_ui(self) -> UIBase:
        mode = get(self.config, "general.mode", "cli")

        if mode == "tui":
            try:
                from sol.ui.tui import TuiUI
                return TuiUI()
            except ImportError:
                pass

        return CliUI()

    def _init_memory(self) -> MemoryStore:
        backend = get(self.config, "memory.backend", "sqlite")

        if backend == "sqlite":
            try:
                from sol.memory.sqlite_store import SqliteMemoryStore
                from sol.memory.migration import maybe_migrate

                db_path = os.path.join(self.base_dir, "sol_memory.db")
                json_path = os.path.join(self.base_dir, "sol_memory.json")

                # Auto-migrate from JSON if needed
                maybe_migrate(json_path, db_path)

                return SqliteMemoryStore(db_path)
            except Exception as e:
                self.ui.display_message(f"SQLite init failed ({e}), using JSON fallback.", "dim")

        # Fallback to JSON
        json_path = os.path.join(self.base_dir, "sol_memory.json")
        return JsonMemoryStore(json_path)

    def _init_brain(self) -> BaseBrain:
        backend = get(self.config, "brain.backend", "auto")

        # Try Gemini cloud first (best quality, free tier)
        if backend in ("gemini", "cloud", "auto"):
            try:
                from sol.brain.gemini_brain import GeminiBrain
                brain = GeminiBrain(self.memory, self.config)
                if brain.is_available():
                    model = get(self.config, "brain.gemini_model", "gemini-2.5-flash")
                    self.brain_name = f"Gemini cloud ({model})"
                    return brain
            except ImportError:
                pass
            except Exception as e:
                self.ui.display_message(f"Gemini init failed: {e}", "dim")

        # Try Ollama (local LLM server)
        if backend in ("ollama", "auto"):
            try:
                from sol.brain.ollama_brain import OllamaBrain
                brain = OllamaBrain(self.memory, self.config)
                if brain.is_available():
                    model = get(self.config, "brain.ollama_model", "gemma3:4b")
                    self.brain_name = f"Ollama local ({model})"
                    return brain
            except ImportError:
                pass
            except Exception as e:
                self.ui.display_message(f"Ollama init failed: {e}", "dim")

        # Try llama-cpp-python (local GGUF model)
        if backend in ("llm", "auto"):
            try:
                from sol.brain.llm_brain import LLMBrain
                model_path = resolve_path(self.config, get(self.config, "brain.llm_model", ""))
                if os.path.exists(model_path):
                    brain = LLMBrain(model_path, self.memory, self.config)
                    if brain.is_available():
                        self.brain_name = "Local LLM (GGUF)"
                        return brain
            except ImportError:
                pass
            except Exception as e:
                self.ui.display_message(f"LLM init failed: {e}", "dim")

        self.brain_name = "Pattern matching"
        return PatternBrain(self.memory)

    def _init_voice_input(self):
        if not get(self.config, "general.voice_input", True):
            return None

        stt = get(self.config, "voice.stt_backend", "auto")

        engine = None

        # Try Whisper first
        if stt in ("whisper", "auto"):
            try:
                from sol.voice.whisper_stt import WhisperSTT
                model_path = resolve_path(self.config, get(self.config, "voice.whisper_model", ""))
                if os.path.exists(model_path):
                    e = WhisperSTT(model_path)
                    if e.is_available():
                        engine = e
                        self.ui.display_message("Voice input: Whisper (ready)", "system")
            except ImportError:
                pass

        # Try Vosk
        if engine is None and stt in ("vosk", "auto"):
            try:
                from sol.voice.vosk_stt import VoskSTT
                model_path = resolve_path(self.config, get(self.config, "voice.vosk_model", ""))
                if not os.path.isdir(model_path):
                    model_path = VoskSTT.find_model(self.base_dir)
                if model_path:
                    e = VoskSTT(model_path)
                    if e.is_available():
                        engine = e
                        self.ui.display_message("Voice input: Vosk (ready)", "system")
            except ImportError:
                pass

        if engine is None:
            self.ui.display_message("No voice input available. Using keyboard.", "dim")
            return None

        # Wrap with push-to-talk so mic is off until space is pressed
        try:
            from sol.voice.push_to_talk import PushToTalk
            ptt = PushToTalk(engine)
            if ptt.is_available():
                self.ui.display_message("Push-to-talk: ON (press SPACE to speak)", "system")
                return ptt
        except ImportError:
            pass

        return engine

    def _init_voice_output(self):
        if not get(self.config, "general.voice_output", True):
            return None

        tts = get(self.config, "voice.tts_backend", "auto")

        # Try Piper first
        if tts in ("piper", "auto"):
            try:
                from sol.voice.piper_tts import PiperTTS
                model_path = resolve_path(self.config, get(self.config, "voice.piper_model", ""))
                if os.path.exists(model_path):
                    engine = PiperTTS(model_path)
                    if engine.is_available():
                        self.ui.display_message("Voice output: Piper (ready)", "system")
                        return engine
            except ImportError:
                pass

        # Try macOS native say
        if tts in ("mac_say", "auto"):
            try:
                from sol.voice.mac_say_tts import MacSayTTS
                voice = get(self.config, "voice.mac_voice", "Daniel")
                rate = get(self.config, "voice.speech_rate", 180)
                engine = MacSayTTS(voice=voice, rate=rate)
                if engine.is_available():
                    self.ui.display_message(f"Voice output: macOS say ({voice})", "system")
                    return engine
            except ImportError:
                pass

        # Try pyttsx3
        if tts in ("pyttsx3", "auto"):
            try:
                from sol.voice.pyttsx3_tts import Pyttsx3TTS
                rate = get(self.config, "voice.speech_rate", 140)
                engine = Pyttsx3TTS(rate=rate)
                if engine.is_available():
                    self.ui.display_message("Voice output: pyttsx3 (ready)", "system")
                    return engine
            except ImportError:
                pass

        self.ui.display_message("No voice output available. Text only.", "dim")
        return None

    def _init_plugins(self) -> list:
        if not get(self.config, "plugins.enabled", True):
            return []

        try:
            from sol.plugins.loader import discover_plugins
            plugin_dir = resolve_path(self.config, get(self.config, "plugins.directory", "plugins"))
            if os.path.isdir(plugin_dir):
                plugins = discover_plugins(plugin_dir, self)
                if plugins:
                    self.ui.display_message(f"Plugins loaded: {len(plugins)}", "system")
                return plugins
        except Exception:
            pass

        return []

    def speak(self, text: str) -> None:
        """Speak text if voice output is available."""
        if self.voice_out:
            self.voice_out.speak(text)

    def listen(self) -> str:
        """Listen for voice input, or fall back to keyboard."""
        if self.voice_in:
            self.ui.display_message("[ Press SPACE to talk... ]", "dim")
            text = self.voice_in.listen()
            if text:
                return text

        return self.ui.get_text_input()

    def _check_reminders(self):
        """Check for pending reminders at session start."""
        if not self.memory.supports_feature("reminders"):
            return
        try:
            from sol.features.reminders import check_pending
            pending = check_pending(self.memory)
            for reminder in pending:
                self.ui.display_message(f"Reminder: {reminder}", "system")
        except Exception:
            pass

    def _generate_greeting(self) -> str:
        """Generate a context-aware greeting."""
        name = self.memory.get_friend_name()

        if name is None:
            return random.choice(FIRST_MEETING)

        # Proactive emotional check-in
        checkin = ""
        try:
            from sol.brain.emotional import get_proactive_checkin
            checkin = get_proactive_checkin(self.memory)
        except ImportError:
            pass

        time_based = ""
        last_talked = self.memory.get_last_talked()
        if last_talked:
            try:
                last = datetime.datetime.fromisoformat(last_talked)
                days = (datetime.datetime.now() - last).days
                if days == 0:
                    time_based = " Back already? I like that."
                elif days == 1:
                    time_based = " Good to see you — been thinking about our last chat."
                elif days <= 7:
                    time_based = f" It's been {days} days. I was starting to wonder."
                elif days > 7:
                    time_based = f" {days} days! I've been here, keeping the lights on."
            except Exception:
                pass

        greetings = [
            f"Hey {name}.{time_based}",
            f"{name}! Good timing.{time_based}",
            f"There you are, {name}.{time_based}",
        ]
        greeting = random.choice(greetings)
        if checkin:
            greeting += f" {checkin}"

        return greeting

    def _get_available_brains(self) -> list:
        """Return list of (key, label) for all available brain backends."""
        available = []

        # Check Gemini
        try:
            from sol.brain.gemini_brain import GeminiBrain
            brain = GeminiBrain(self.memory, self.config)
            if brain.is_available():
                model = get(self.config, "brain.gemini_model", "gemini-2.5-flash")
                available.append(("gemini", f"Gemini cloud ({model})"))
        except (ImportError, Exception):
            pass

        # Check Ollama
        try:
            from sol.brain.ollama_brain import OllamaBrain
            brain = OllamaBrain(self.memory, self.config)
            if brain.is_available():
                model = get(self.config, "brain.ollama_model", "gemma3:4b")
                available.append(("ollama", f"Ollama local ({model})"))
        except (ImportError, Exception):
            pass

        # Check llama-cpp
        try:
            from sol.brain.llm_brain import LLMBrain
            model_path = resolve_path(self.config, get(self.config, "brain.llm_model", ""))
            if os.path.exists(model_path):
                brain = LLMBrain(model_path, self.memory, self.config)
                if brain.is_available():
                    available.append(("llm", "Local LLM (GGUF)"))
        except (ImportError, Exception):
            pass

        # Pattern matching is always available
        available.append(("pattern", "Pattern matching"))

        return available

    def _switch_brain(self, key: str) -> bool:
        """Switch to a specific brain backend. Returns True on success."""
        try:
            if key == "gemini":
                from sol.brain.gemini_brain import GeminiBrain
                brain = GeminiBrain(self.memory, self.config)
                if brain.is_available():
                    self.brain = brain
                    model = get(self.config, "brain.gemini_model", "gemini-2.5-flash")
                    self.brain_name = f"Gemini cloud ({model})"
                    return True
            elif key == "ollama":
                from sol.brain.ollama_brain import OllamaBrain
                brain = OllamaBrain(self.memory, self.config)
                if brain.is_available():
                    self.brain = brain
                    model = get(self.config, "brain.ollama_model", "gemma3:4b")
                    self.brain_name = f"Ollama local ({model})"
                    return True
            elif key == "llm":
                from sol.brain.llm_brain import LLMBrain
                model_path = resolve_path(self.config, get(self.config, "brain.llm_model", ""))
                brain = LLMBrain(model_path, self.memory, self.config)
                if brain.is_available():
                    self.brain = brain
                    self.brain_name = "Local LLM (GGUF)"
                    return True
            elif key == "pattern":
                self.brain = PatternBrain(self.memory)
                self.brain_name = "Pattern matching"
                return True
        except (ImportError, Exception):
            pass
        return False

    def _handle_model_switch(self) -> str:
        """Interactive model switch — returns SOL's response."""
        available = self._get_available_brains()

        if len(available) <= 1:
            return "You've only got one brain available right now. Can't exactly downgrade from here."

        # Build the menu
        lines = ["Right then, here's what I've got:"]
        for i, (key, label) in enumerate(available, 1):
            marker = " (current)" if label == self.brain_name else ""
            lines.append(f"  {i}. {label}{marker}")
        lines.append("")
        lines.append("Say the number or name of the one you want.")

        menu_text = "\n".join(lines)
        self.ui.display_message(menu_text, "sol")
        self.speak("Which brain do you want me to use? Say the number.")
        print()

        # Get user choice
        choice_text = self.listen()
        if not choice_text:
            return "Nothing? Alright, keeping the current brain."

        if self.voice_in:
            self.ui.display_message(choice_text, "you")
            print()

        choice = choice_text.lower().strip()

        # Word-to-number mapping (handles "two", "number two", "the second one", etc.)
        word_to_num = {
            "1": 1, "one": 1, "first": 1, "1st": 1,
            "2": 2, "two": 2, "to": 2, "too": 2, "second": 2, "2nd": 2,
            "3": 3, "three": 3, "third": 3, "3rd": 3,
            "4": 4, "four": 4, "for": 4, "fourth": 4, "4th": 4,
            "5": 5, "five": 5, "fifth": 5, "5th": 5,
        }

        # Extract a number from the choice text
        picked = None
        for word in choice.split():
            if word in word_to_num:
                picked = word_to_num[word]
                break

        if picked and 1 <= picked <= len(available):
            key, label = available[picked - 1]
            if label == self.brain_name:
                return f"Already running {label}. No change needed."
            if self._switch_brain(key):
                return f"Done. Switched to {self.brain_name}. Let's see if I'm smarter now."
            return f"Couldn't switch to {label}. Something went wrong."

        # Match by keyword (gemini, ollama, local, pattern, etc.)
        for key, label in available:
            if key in choice or any(w in choice for w in label.lower().split()):
                if label == self.brain_name:
                    return f"Already running {label}. No change needed."
                if self._switch_brain(key):
                    return f"Done. Switched to {self.brain_name}. Let's see if I'm smarter now."
                return f"Couldn't switch to {label}. Something went wrong."

        return "Didn't catch which one you meant. Try again — say 'change model' whenever."

    def run(self):
        """Main application loop."""
        self.ui.display_banner(brain_name=self.brain_name)

        # Increment conversation count
        self.memory.increment_conversations()
        self.ui.display_status(self.memory.get_metadata())

        # Separator
        from sol.ui.colors import C
        print(f"\n  {C.GRAY}{'─' * 55}{C.RESET}\n")

        # Check pending reminders
        self._check_reminders()

        # Greeting
        greeting = self._generate_greeting()
        self.ui.display_message(greeting, "sol")
        self.speak(greeting)
        print()

        # Conversation loop
        try:
            while True:
                user_text = self.listen()

                if not user_text:
                    continue

                # Display what user said (if voice input was used)
                if self.voice_in:
                    self.ui.display_message(user_text, "you")
                print()

                # Check for model switch command
                lower = user_text.lower()
                if any(phrase in lower for phrase in (
                    "change model", "switch model", "change brain",
                    "switch brain", "change ai", "switch ai",
                )):
                    response = self._handle_model_switch()
                    self.ui.display_message(response, "sol")
                    self.speak(response)
                    print()
                    continue

                # Run plugin on_user_input hooks
                plugin_override = None
                for plugin in self.plugins:
                    try:
                        result = plugin.on_user_input(user_text)
                        if result is not None:
                            plugin_override = result
                            break
                    except Exception:
                        pass

                # Get response
                if plugin_override is not None:
                    response = plugin_override
                else:
                    response = self.brain.think(user_text)

                # Run plugin on_response hooks
                for plugin in self.plugins:
                    try:
                        response = plugin.on_response(user_text, response)
                    except Exception:
                        pass

                # Display + speak
                self.ui.display_message(response, "sol")
                self.speak(response)
                print()

                # Check for exit
                if any(w in user_text.lower() for w in GOODBYE_WORDS):
                    self.memory.set_last_talked(datetime.datetime.now().isoformat())
                    time.sleep(1)
                    self.ui.display_message("[ Session saved. See you next time. ]", "system")
                    print()

                    # Generate session summary
                    try:
                        from sol.features.journal import generate_session_summary
                        generate_session_summary(self.brain.get_context(), self.memory)
                    except Exception:
                        pass

                    # Run plugin on_session_end hooks
                    for plugin in self.plugins:
                        try:
                            plugin.on_session_end()
                        except Exception:
                            pass
                    break

        except KeyboardInterrupt:
            print()
            farewell = "Heading out? No worries — I'll remember where we left off."
            self.ui.display_message(farewell, "sol")
            self.speak(farewell)
            self.memory.set_last_talked(datetime.datetime.now().isoformat())
            self.ui.display_message("[ Session saved. See you next time. ]", "system")
            print()
