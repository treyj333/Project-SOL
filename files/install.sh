#!/bin/bash
# ============================================================
#  SOL Installer — sets up everything needed to run SOL
#  Usage: curl the repo, then run: bash install.sh
# ============================================================

set -e

BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
CYAN="\033[36m"
RESET="\033[0m"

echo ""
echo -e "${CYAN}${BOLD}    ███████╗ ██████╗ ██╗     ${RESET}"
echo -e "${CYAN}${BOLD}    ██╔════╝██╔═══██╗██║     ${RESET}"
echo -e "${CYAN}${BOLD}    ███████╗██║   ██║██║     ${RESET}"
echo -e "${CYAN}${BOLD}    ╚════██║██║   ██║██║     ${RESET}"
echo -e "${CYAN}${BOLD}    ███████║╚██████╔╝███████╗${RESET}"
echo -e "${CYAN}${BOLD}    ╚══════╝ ╚═════╝ ╚══════╝${RESET}"
echo ""
echo -e "${BOLD}SOL Installer${RESET} — Your AI Companion"
echo "============================================"
echo ""

# ----------------------------------------------------------
# 1. Check OS
# ----------------------------------------------------------
OS="$(uname -s)"
echo -e "${CYAN}[1/7]${RESET} Detecting platform..."

if [ "$OS" = "Darwin" ]; then
    echo -e "  ${GREEN}✓${RESET} macOS detected"
elif [ "$OS" = "Linux" ]; then
    echo -e "  ${GREEN}✓${RESET} Linux detected"
else
    echo -e "  ${YELLOW}!${RESET} $OS detected — SOL works best on macOS/Linux"
fi

# ----------------------------------------------------------
# 2. Check Python
# ----------------------------------------------------------
echo ""
echo -e "${CYAN}[2/7]${RESET} Checking Python..."

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
            PYTHON="$cmd"
            echo -e "  ${GREEN}✓${RESET} $cmd ($("$cmd" --version 2>&1))"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo -e "  ${RED}✗${RESET} Python 3.9+ not found."
    echo "    Install Python: https://python.org/downloads"
    exit 1
fi

# ----------------------------------------------------------
# 3. Check/install pip
# ----------------------------------------------------------
echo ""
echo -e "${CYAN}[3/7]${RESET} Checking pip..."

if $PYTHON -m pip --version &>/dev/null; then
    echo -e "  ${GREEN}✓${RESET} pip available"
else
    echo -e "  ${YELLOW}!${RESET} pip not found, installing..."
    $PYTHON -m ensurepip --upgrade 2>/dev/null || {
        echo -e "  ${RED}✗${RESET} Could not install pip. Install it manually."
        exit 1
    }
fi

# ----------------------------------------------------------
# 4. Install SOL package
# ----------------------------------------------------------
echo ""
echo -e "${CYAN}[4/7]${RESET} Installing SOL..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

$PYTHON -m pip install -e "." --quiet 2>&1 | tail -1
echo -e "  ${GREEN}✓${RESET} SOL core installed"

# ----------------------------------------------------------
# 5. Install voice dependencies (platform-specific)
# ----------------------------------------------------------
echo ""
echo -e "${CYAN}[5/7]${RESET} Installing voice dependencies..."

if [ "$OS" = "Darwin" ]; then
    # macOS: TTS works out of the box (say command)
    echo -e "  ${GREEN}✓${RESET} Voice output: macOS say (built-in)"

    # Check for Homebrew (needed for portaudio)
    if command -v brew &>/dev/null; then
        if ! brew list portaudio &>/dev/null 2>&1; then
            echo "  Installing portaudio via Homebrew..."
            brew install portaudio --quiet
        fi
        echo -e "  ${GREEN}✓${RESET} portaudio installed"
    else
        echo -e "  ${YELLOW}!${RESET} Homebrew not found — voice input needs portaudio"
        echo "    Install Homebrew: https://brew.sh"
        echo "    Then run: brew install portaudio"
    fi
elif [ "$OS" = "Linux" ]; then
    if command -v apt-get &>/dev/null; then
        echo "  Installing portaudio via apt..."
        sudo apt-get install -y portaudio19-dev python3-pyaudio --quiet 2>/dev/null || true
    elif command -v dnf &>/dev/null; then
        echo "  Installing portaudio via dnf..."
        sudo dnf install -y portaudio-devel --quiet 2>/dev/null || true
    fi
fi

# Install Python voice packages
$PYTHON -m pip install vosk sounddevice numpy --quiet 2>&1 | tail -1
echo -e "  ${GREEN}✓${RESET} Voice input packages installed (vosk, sounddevice, numpy)"

# ----------------------------------------------------------
# 6. Download Vosk model
# ----------------------------------------------------------
echo ""
echo -e "${CYAN}[6/7]${RESET} Checking speech model..."

MODEL_DIR="$SCRIPT_DIR/models"
MODEL_NAME="vosk-model-small-en-us-0.15"

if [ -d "$MODEL_DIR/$MODEL_NAME" ]; then
    echo -e "  ${GREEN}✓${RESET} Vosk model already downloaded"
else
    mkdir -p "$MODEL_DIR"
    echo "  Downloading Vosk English model (~50MB)..."
    if command -v curl &>/dev/null; then
        curl -L --progress-bar \
            "https://alphacephei.com/vosk/models/${MODEL_NAME}.zip" \
            -o "$MODEL_DIR/${MODEL_NAME}.zip"
    elif command -v wget &>/dev/null; then
        wget -q --show-progress \
            "https://alphacephei.com/vosk/models/${MODEL_NAME}.zip" \
            -O "$MODEL_DIR/${MODEL_NAME}.zip"
    else
        echo -e "  ${RED}✗${RESET} Neither curl nor wget found. Download manually:"
        echo "    https://alphacephei.com/vosk/models/${MODEL_NAME}.zip"
    fi

    if [ -f "$MODEL_DIR/${MODEL_NAME}.zip" ]; then
        echo "  Extracting model..."
        unzip -q "$MODEL_DIR/${MODEL_NAME}.zip" -d "$MODEL_DIR"
        rm "$MODEL_DIR/${MODEL_NAME}.zip"
        echo -e "  ${GREEN}✓${RESET} Vosk model ready"
    fi
fi

# ----------------------------------------------------------
# 7. Setup check + optional Ollama/Gemini
# ----------------------------------------------------------
echo ""
echo -e "${CYAN}[7/7]${RESET} Checking AI backends..."

BRAIN_FOUND=false

# Check for .env with Gemini key
if [ -f "$SCRIPT_DIR/.env" ] && grep -q "GEMINI_API_KEY" "$SCRIPT_DIR/.env" 2>/dev/null; then
    echo -e "  ${GREEN}✓${RESET} Gemini API key found in .env"
    BRAIN_FOUND=true
fi

# Check for Ollama
if command -v ollama &>/dev/null; then
    echo -e "  ${GREEN}✓${RESET} Ollama installed"
    if ollama list 2>/dev/null | grep -q "gemma3"; then
        echo -e "  ${GREEN}✓${RESET} gemma3 model available"
    else
        echo -e "  ${YELLOW}!${RESET} No gemma3 model. Pull one with: ollama pull gemma3:4b"
    fi
    BRAIN_FOUND=true
fi

if [ "$BRAIN_FOUND" = false ]; then
    echo ""
    echo -e "  ${YELLOW}!${RESET} No AI backend configured. SOL will use pattern matching."
    echo "    For cloud AI (free): Get a Gemini API key at https://aistudio.google.com"
    echo "      Then create .env with: GEMINI_API_KEY=your-key-here"
    echo "    For local AI: Install Ollama at https://ollama.com"
    echo "      Then run: ollama pull gemma3:4b"
fi

# ----------------------------------------------------------
# Done!
# ----------------------------------------------------------
echo ""
echo "============================================"
echo -e "${GREEN}${BOLD}SOL is ready!${RESET}"
echo ""
echo -e "  Run SOL:  ${BOLD}$PYTHON sol.py${RESET}"
echo ""
echo "  Voice: Press SPACE to talk, SOL responds out loud"
echo "  Quit:  Say 'goodbye' or press Ctrl+C"
echo ""
echo "============================================"
echo ""
