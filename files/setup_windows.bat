@echo off
REM ═══════════════════════════════════════════════════════════════
REM  SOL v2.0 Setup Script for Windows — Run this once
REM ═══════════════════════════════════════════════════════════════

echo.
echo   ███████╗ ██████╗ ██╗
echo   ██╔════╝██╔═══██╗██║
echo   ███████╗██║   ██║██║
echo   ╚════██║██║   ██║██║
echo   ███████║╚██████╔╝███████╗
echo   ╚══════╝ ╚═════╝ ╚══════╝
echo.
echo   Setting up your AI friend (v2.0)...
echo   ─────────────────────────────
echo.

REM Check Python
echo [1/3] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ERROR: Python not found!
    echo   Install Python 3.8+ from https://python.org
    echo   Make sure to check "Add Python to PATH" during install!
    pause
    exit /b 1
)
python --version
echo.

REM Install dependencies
echo [2/3] Installing Python packages...
python -m pip install --upgrade pip
python -m pip install vosk pyttsx3 sounddevice numpy
echo.
echo   Optional extras:
echo     python -m pip install llama-cpp-python   (LLM brain)
echo     python -m pip install textual            (Rich TUI)
echo     python -m pip install piper-tts          (Natural voice)
echo.
echo   Done!
echo.

REM Download Vosk model
echo [3/3] Setting up speech recognition model...
if exist "models\vosk-model-small-en-us-0.15" (
    echo   Model already exists. Good!
) else (
    mkdir models 2>nul
    echo   Download the speech model manually:
    echo.
    echo   1. Go to: https://alphacephei.com/vosk/models
    echo   2. Download: vosk-model-small-en-us-0.15.zip
    echo   3. Extract to: %cd%\models\vosk-model-small-en-us-0.15\
    echo.
    echo   This is the only time you need internet!
)
echo.

echo   ─────────────────────────────
echo   Setup complete!
echo.
echo   To start SOL, run:
echo     python sol.py
echo.
echo   Configure SOL by editing sol.toml
echo   Or double-click: START_SOL.bat
echo   ─────────────────────────────
echo.
pause
