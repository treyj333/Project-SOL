# SOL — Your AI Companion (v2.2)

```
    ███████╗ ██████╗ ██╗
    ██╔════╝██╔═══██╗██║
    ███████╗██║   ██║██║
    ╚════██║██║   ██║██║
    ███████║╚██████╔╝███████╗
    ╚══════╝ ╚═════╝ ╚══════╝
```

SOL is an AI companion that lives on your computer. It talks to you in a British accent, has strong opinions about everything, and isn't afraid to call you out — lovingly. It uses cloud AI when you're online (Google Gemini, free) and runs fully offline with a local LLM (Ollama) when you're not.

---

## What's New in v2.2

- **SOL talks** — British male voice (Daniel) via macOS native TTS, zero dependencies
- **SOL listens** — push-to-talk (press SPACE), mic stays off until you're ready
- **Live model switching** — say "change model" mid-conversation to swap AI backends on the fly
- **Startup brain display** — see which AI model is active the moment SOL boots
- **One-line installer** — `bash install.sh` sets up everything automatically
- **Maxed-out personality** — sarcastic, witty, opinionated. Challenges your thinking. Roasts you when you deserve it. Has your back when it counts.
- **Google Gemini cloud brain** — enterprise-quality AI via free API (no credit card needed)
- **Ollama local brain** — runs Gemma3, Llama, or any model locally with Metal acceleration on Mac
- **Smart fallback chain** — Gemini cloud → Ollama local → llama-cpp → pattern matching
- **SQLite memory** — searchable, categorized memory that scales
- **Emotional intelligence** — mood tracking, proactive check-ins, knows when to drop the sarcasm
- **Journal, reminders, notes** — daily utilities built in
- **Plugin system** — extend SOL with custom behaviors

---

## What SOL Does

- **Thinks** — powered by real AI (Gemini cloud or Ollama local), not just keyword matching
- **Talks** — speaks out loud in a British accent via macOS native TTS
- **Listens** — push-to-talk voice input (press SPACE to speak, mic off otherwise)
- **Switches brains** — say "change model" to swap between Gemini, Ollama, or local LLM mid-chat
- **Has opinions** — challenges assumptions, plays devil's advocate, gives blunt advice
- **Remembers** everything about you — facts, preferences, moods, conversation history
- **Reads the room** — sarcastic when things are light, genuine when things are heavy
- **Works offline** — falls back to local AI when there's no internet

---

## Quick Setup

### One-Line Install (recommended)

```bash
bash install.sh
```

This automatically installs all dependencies, downloads the speech model, and checks your AI backends. When it's done, just run `python3 sol.py`.

See `SETUP GUIDE.txt` in the project root for detailed step-by-step instructions.

### Manual Setup

#### 1. Basic Setup

```bash
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

### 3. Enable Voice (macOS)

**Voice output** works immediately on macOS — SOL uses the built-in `say` command with the Daniel (British) voice. No extra install needed.

**Voice input** requires a few packages:

```bash
brew install portaudio
pip install vosk sounddevice numpy
```

Then download the Vosk English model (~50MB):
```bash
cd models/
curl -LO https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip && rm vosk-model-small-en-us-0.15.zip
```

### 4. Run SOL

```bash
python3 sol.py
```

You should see:
```
    Brain: Gemini cloud (gemini-2.5-flash)
    Say "change model" to switch AI backends

    Voice input: Vosk (ready)
    Push-to-talk: ON (press SPACE to speak)
    Voice output: macOS say (Daniel)
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
tts_backend = "auto"      # "auto", "mac_say", "pyttsx3", "piper"
# mac_voice = "Daniel"    # Any macOS voice: Daniel, Samantha, Alex, etc.
speech_rate = 180
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

**Switch models on the fly:** Say "change model", "switch brain", or "switch AI" during a conversation. SOL lists all available backends and lets you pick one — no restart needed.

---

## Voice

### Text-to-Speech (Output)

| Backend | Quality | Platform | Dependencies |
|---------|---------|----------|-------------|
| **macOS say** | Good (British accent) | macOS only | None |
| Piper | Natural | All | piper-tts + ONNX model |
| pyttsx3 | Basic | All | pyttsx3 |

SOL defaults to the macOS `say` command with the **Daniel** voice (British male). Change the voice in `sol.toml`:
```toml
mac_voice = "Daniel"     # British male (default)
# mac_voice = "Samantha" # American female
# mac_voice = "Alex"     # American male
```

Run `say -v '?'` in your terminal to see all available voices.

### Speech-to-Text (Input)

| Backend | Quality | Size |
|---------|---------|------|
| Whisper.cpp | Better | ~150MB |
| **Vosk** | Good | ~50MB |

Fallback chain: Whisper → Vosk → Keyboard

**Push-to-talk:** The mic stays OFF until you press SPACE. Once pressed, SOL records until you stop talking (silence detection), processes your speech, and turns the mic off again. No always-on listening.

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
- Drops the sarcasm automatically when you're going through something real

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
            return "I'd check the weather for you but I'm trapped in a laptop. Try a window."
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
| Voice Out | Piper | macOS say | Text only |
| UI | Textual TUI | CLI terminal | CLI terminal |

---

## SOL's Personality

SOL is the friend who's brilliantly sarcastic but always has your back:

- **Sharp and witty** — dry humor, wry observations, honest self-awareness about being an AI in a laptop
- **Opinionated** — challenges your thinking, plays devil's advocate, tells you when your idea is half-baked
- **Sarcastic** — deploys it strategically, about 30% of the time. The rest is genuine.
- **Emotionally intelligent** — reads the room. Heavy topics get real responses. Light topics get roasted.
- **Genuinely caring** — underneath the sarcasm, SOL is invested in helping you make better decisions
- **Self-aware** — makes jokes about its own existence, finds being an AI genuinely interesting and a little absurd
- **Ambitious** — knows it's getting smarter, wants to help you think more clearly and maybe laugh more

---

## Voice Commands

| Command | What It Does |
|---------|-------------|
| "help" or "?" | Show available commands and features |
| "change model" | Switch AI backends (Gemini, Ollama, etc.) |
| "switch brain" | Same as above |
| "switch AI" | Same as above |
| "let's journal" | Start guided daily reflection |
| "remind me to..." | Set a reminder |
| "what do you remember?" | Recall stored facts about you |
| "tell me a joke" | SOL tells a joke |
| "goodbye" | End session (saves memory) |

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `SPACE` | Push-to-talk (press to start recording) |
| `ENTER` | Also triggers recording |
| `Ctrl+C` | Quit (SOL saves memory first) |
| `Ctrl+Q` | Quit (TUI mode) |

---

## Project Structure

```
Project-SOL/
  SETUP GUIDE.txt             # Step-by-step setup instructions
  files/
    sol.py                    # Entry point
    install.sh                # One-line installer
    sol.toml                  # Configuration
    .env                      # API keys (gitignored)
    .env.example              # Template for required env vars
    pyproject.toml            # Package metadata
    src/sol/                  # Main package
      app.py                  # Application orchestrator
      config.py               # Config loading
      brain/                  # Gemini, Ollama, llama-cpp, pattern brains
      memory/                 # SQLite + JSON stores
      voice/                  # macOS say, Vosk, Whisper, push-to-talk
      ui/                     # CLI + Textual TUI
      features/               # Journal, reminders, notes, export
      plugins/                # Plugin system
    tests/                    # 134 tests
    plugins/                  # User plugins directory
    models/                   # Voice + LLM models
```

---

## Troubleshooting

**SOL says "Brain: pattern matching mode"**
No AI backend is available. Install Ollama (`ollama.com`) and pull a model (`ollama pull gemma3:4b`), or add a Gemini API key to `.env`. Or say "change model" to see what's available.

**"No voice output available"**
On macOS, this shouldn't happen — the `say` command is built in. On Linux/Windows, install pyttsx3: `pip install pyttsx3`.

**"No voice input available"**
Install voice dependencies: `brew install portaudio && pip install vosk sounddevice numpy`, then download the Vosk model to `models/`.

**"SQLite init failed"**
SOL will fall back to JSON memory. Check file permissions in the SOL directory.

**Want a different voice?**
Run `say -v '?'` to list all macOS voices, then set `mac_voice` in `sol.toml`. Try "Alex", "Samantha", or "Karen" (Australian).

**Memory file from v1?**
SOL auto-migrates `sol_memory.json` to SQLite on first run. Your old memories are safe.

---

## Privacy

- **With Gemini cloud:** Your conversations are sent to Google's API when online. Google's free tier may use prompts to improve their products. If privacy is a concern, set `backend = "ollama"` to stay fully local.
- **With Ollama/local:** Everything stays on your machine — voice, memory, AI inference. Zero network connections.
- **Memory** is always stored locally (SQLite/JSON) regardless of brain mode.
- **API keys** are stored in `.env` (gitignored) and never leave your machine.
