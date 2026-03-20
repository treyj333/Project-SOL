#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  SOL v2.0 Setup Script — Run this once on your machine
# ═══════════════════════════════════════════════════════════════

set -e

echo ""
echo "  ███████╗ ██████╗ ██╗     "
echo "  ██╔════╝██╔═══██╗██║     "
echo "  ███████╗██║   ██║██║     "
echo "  ╚════██║██║   ██║██║     "
echo "  ███████║╚██████╔╝███████╗"
echo "  ╚══════╝ ╚═════╝ ╚══════╝"
echo ""
echo "  Setting up your AI friend (v2.0)..."
echo "  ─────────────────────────────"
echo ""

# Check Python
echo "[1/4] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "  ERROR: Python not found!"
    echo "  Install Python 3.8+ from https://python.org"
    exit 1
fi

echo "  Found: $($PYTHON --version)"
echo ""

# Install core dependencies
echo "[2/4] Installing Python packages..."
echo "  (This works offline if you have the .whl files)"
$PYTHON -m pip install --upgrade pip 2>/dev/null || true
$PYTHON -m pip install vosk pyttsx3 sounddevice numpy
echo ""
echo "  Want smarter conversations? Install the LLM brain:"
echo "    $PYTHON -m pip install llama-cpp-python"
echo ""
echo "  Want a nicer UI? Install the TUI:"
echo "    $PYTHON -m pip install textual"
echo ""
echo "  Want better voice? Install Whisper + Piper:"
echo "    $PYTHON -m pip install whisper-cpp-python piper-tts"
echo ""
echo "  Done!"
echo ""

# Download Vosk model
echo "[3/4] Setting up speech recognition model..."
MODELS_DIR="$(dirname "$0")/models"
MODEL_DIR="$MODELS_DIR/vosk-model-small-en-us-0.15"

if [ -d "$MODEL_DIR" ]; then
    echo "  Model already exists. Good!"
else
    mkdir -p "$MODELS_DIR"
    echo "  Downloading small English model (~50MB)..."
    echo "  (You only need internet for this one download)"
    echo ""

    if command -v wget &> /dev/null; then
        wget -q --show-progress -O "$MODELS_DIR/model.zip" \
            "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    elif command -v curl &> /dev/null; then
        curl -L -o "$MODELS_DIR/model.zip" \
            "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    else
        echo "  ERROR: wget or curl not found."
        echo "  Download manually from:"
        echo "    https://alphacephei.com/vosk/models"
        echo "  Extract to: $MODEL_DIR"
        exit 1
    fi

    echo "  Extracting..."
    cd "$MODELS_DIR"
    unzip -q model.zip
    rm model.zip
    cd - > /dev/null
    echo "  Done!"
fi
echo ""

# Verify microphone
echo "[4/4] Checking microphone..."
$PYTHON -c "
import sounddevice as sd
devices = sd.query_devices()
has_input = any(d['max_input_channels'] > 0 for d in devices)
if has_input:
    default = sd.query_devices(kind='input')
    print(f\"  Microphone found: {default['name']}\")
    print('  Ready!')
else:
    print('  WARNING: No microphone detected.')
    print('  SOL will use keyboard input instead.')
" 2>/dev/null || echo "  Could not check microphone. SOL will try at runtime."

echo ""
echo "  ─────────────────────────────"
echo "  Setup complete!"
echo ""
echo "  To start SOL, run:"
echo "    $PYTHON sol.py"
echo ""
echo "  Configure SOL by editing sol.toml"
echo "  Memory auto-migrates from v1 on first run."
echo "  No internet needed after this setup!"
echo "  ─────────────────────────────"
echo ""
