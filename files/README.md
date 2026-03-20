# SOL — Your AI Companion (v2.1)

```
    ███████╗ ██████╗ ██╗
    ██╔════╝██╔═══██╗██║
    ███████╗██║   ██║██║
    ╚════██║██║   ██║██║
    ███████║╚██████╔╝███████╗
    ╚══════╝ ╚═════╝ ╚══════╝
```

SOL is an AI companion that lives on your computer. It uses cloud AI when you're online (Google Gemini, free) and runs fully offline with a local LLM (Ollama) when you're not. SOL remembers your conversations, tracks your mood, and actually tries to be useful — not just friendly.

---

## What's New in v2.1

- **Google Gemini cloud brain** — enterprise-quality AI via free API (no credit card needed)
- **Ollama local brain** — runs Gemma3, Llama, or any local model via Ollama with Metal acceleration on Mac
- **Smart fallback chain** — Gemini cloud → Ollama local → llama-cpp → pattern matching
- **Real personality** — SOL has opinions, asks probing questions, pushes back when something doesn't add up
- **SQLite memory** — searchable, categorized memory that scales
- **Emotional intelligence** — mood tracking, proactive check-ins, relationship depth
- **Rich TUI** — terminal UI with chat panel and memory sidebar
- **Voice I/O** — Whisper.cpp for accuracy, Piper for natural speech
- **Journal, reminders, notes** — daily utilities built in
- **Plugin system** — extend SOL with custom behaviors

---

## What SOL Does

- **Thinks** — powered by real AI (Gemini cloud or Ollama local), not just keyword matching
- **Adds value** — offers perspectives, asks follow-up questions, challenges assumptions
- **Remembers** everything about you — facts, preferences, moods, conversation history
- **Listens** via microphone (or keyboard) and responds with voice (or text)
- **Tracks your mood** and checks in on you next session
- **Journals, reminds, and takes notes** for daily utility
- **Works offline** — falls back to local AI when there's no internet

---

## Quick Setup

### 1. Basic Setup

```bash
# Clone and enter the project
cd files/
pip install -e "."
```

### 2. Connect a Brain (pick one or both)

**Option A: Google Gemini (cloud, free)**
1. Get a free API key at [aistudio.google.com](https://aistudio.google.com)
2. Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your-key-here
   ```
3. Run SOL — it'll use Gemini automatically when online

**Option B: Ollama (local, offline)**
1. Install Ollama: [ollama.com](https://ollama.com)
2. Pull a model: `ollama pull gemma3:4b` (~3.3GB)
3. Run SOL — it'll detect Ollama automatically

**Both together (recommended):** Set up both. SOL uses Gemini when online and falls back to Ollama when offline.

### 3. Run SOL

```bash
python3 sol.py
```

### Optional Extras

```bash
pip install -e ".[voice]"    # Vosk + sounddevice for voice input
pip install -e ".[llm]"      # llama-cpp-python for GGUF models
pip install -e ".[tui]"      # Rich TUI via Textual
pip install -e ".[whisper]"  # Whisper.cpp for better voice recognition
pip install -e ".[piper]"    # Piper for natural text-to-speech
pip install -e ".[all]"      # Everything
```

---

## Configuration

Edit `sol.toml` to customize SOL:

```toml
[general]
mode = "cli"              # "cli" or "tui"
voice_input = true
voice_output = true

[brain]
backend = "auto"          # "auto", "gemini", "cloud", "ollama", "llm", "pattern"
# gemini_api_key = ""     # Or use .env file / GEMINI_API_KEY env var
# gemini_model = "gemini-2.5-flash"
ollama_model = "gemma3:4b"
# temperature = 0.7

[voice]
stt_backend = "auto"      # "auto", "vosk", "whisper"
tts_backend = "auto"      # "auto", "pyttsx3", "piper"
wake_word = false

[memory]
backend = "sqlite"        # "sqlite" or "json"

[features]
journal = true
reminders = true
notes = true
```

---

## Brain Modes

| Mode | Quality | Speed | Requires |
|------|---------|-------|----------|
| **Gemini cloud** | Best | Fast | Internet + free API key |
| **Ollama local** | Great | Good (Metal on Mac) | Ollama + model downloaded |
| **llama-cpp** | Good | Varies | GGUF model file |
| **Pattern matching** | Basic | Instant | Nothing |

SOL tries each in order and uses the best available. Set `backend = "ollama"` in `sol.toml` to force a specific mode.

---

## Features

### Memory System
- **SQLite** (default) — searchable facts, preferences, moods, conversation summaries
- **JSON** (fallback) — simple file-based storage, backward compatible with v1
- Auto-migrates your v1 `sol_memory.json` to SQLite on first run

### Emotional Intelligence
- Detects 6 mood categories: happy, sad, anxious, angry, excited, neutral
- Tracks mood intensity over time
- Proactive check-ins when you return after a rough session
- Relationship depth score that grows the more you talk

### Voice

| Backend | Quality | Size |
|---------|---------|------|
| Vosk | Good | ~50MB |
| Whisper.cpp | Better | ~150MB |
| pyttsx3 | Basic TTS | 0MB |
| Piper | Natural TTS | ~50MB |

### Daily Utilities
- **Journal mode** — "Let's journal" starts guided reflection
- **Reminders** — "Remind me to call mom tomorrow"
- **Quick notes** — "Remember that my dentist is on Tuesday"
- **Memory recall** — "What did I tell you about the dentist?"

### Plugin System

Create `plugins/my_plugin/plugin.py`:

```python
from sol.plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    @property
    def name(self):
        return "my_plugin"

    def on_user_input(self, text):
        if "weather" in text:
            return "I can't check the weather yet — but I'm working on it."
        return None
```

### Export

```bash
python3 -c "
from sol.memory.sqlite_store import SqliteMemoryStore
from sol.features.export import save_export
store = SqliteMemoryStore('sol_memory.db')
save_export(store, 'sol_export.md', 'markdown')
"
```

---

## Graceful Degradation

SOL always works. Every optional feature falls back gracefully:

| Component | Best | Fallback | Minimum |
|-----------|------|----------|---------|
| Brain | Gemini cloud | Ollama local | Pattern matching |
| Memory | SQLite | JSON file | JSON file |
| Voice In | Whisper.cpp | Vosk | Keyboard |
| Voice Out | Piper | pyttsx3 | Text only |
| UI | Textual TUI | CLI terminal | CLI terminal |

---

## SOL's Personality

SOL is a thoughtful, grounded AI companion:

- Genuine curiosity about people and their decisions
- Offers perspectives and asks probing questions — not just a yes-man
- Dry, warm humor and honest self-awareness
- Pushes back gently when something doesn't add up
- Connects dots across conversations
- Honest about limitations — frames them as things being worked on
- Ambitious about becoming more capable over time

---

## Project Structure

```
files/
  sol.py                    # Entry point (backward compatible)
  sol.toml                  # Configuration
  .env                      # API keys (gitignored)
  pyproject.toml            # Package metadata
  src/sol/                  # Main package
    app.py                  # Application orchestrator
    config.py               # Config loading
    brain/                  # Gemini, Ollama, llama-cpp, pattern brains
    memory/                 # SQLite + JSON stores
    voice/                  # Vosk, Whisper, pyttsx3, Piper
    ui/                     # CLI + Textual TUI
    features/               # Journal, reminders, notes, export
    plugins/                # Plugin system
  tests/                    # 120 tests
  plugins/                  # User plugins directory
  models/                   # Voice + LLM models
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+C` | Quit (SOL saves memory first) |
| Say "goodbye" | Graceful exit |
| `Ctrl+Q` | Quit (TUI mode) |

---

## Troubleshooting

**SOL says "Brain: pattern matching mode"**
No AI backend is available. Install Ollama (`ollama.com`) and pull a model (`ollama pull gemma3:4b`), or add a Gemini API key to `.env`.

**"No voice input available"**
Install voice dependencies: `pip install -e ".[voice]"` and download a Vosk model.

**"SQLite init failed"**
SOL will fall back to JSON memory. Check file permissions in the SOL directory.

**Want better voice quality?**
Install Piper for natural TTS: `pip install piper-tts` and download a voice model.

**Memory file from v1?**
SOL auto-migrates `sol_memory.json` to SQLite on first run. Your old memories are safe.

---

## Privacy

- **With Gemini cloud:** Your conversations are sent to Google's API when online. Google's free tier may use prompts to improve their products. If privacy is a concern, set `backend = "ollama"` to stay fully local.
- **With Ollama/local:** Everything stays on your machine — voice, memory, AI inference. Zero network connections.
- **Memory** is always stored locally (SQLite/JSON) regardless of brain mode.
- **API keys** are stored in `.env` (gitignored) and never leave your machine.
