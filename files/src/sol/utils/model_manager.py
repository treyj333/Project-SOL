"""Model download and management utilities."""

import os
import sys
import urllib.request
import zipfile
import shutil

# Default model URLs
MODELS = {
    "vosk": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "dest": "models/vosk-model-small-en-us-0.15",
        "size": "~50MB",
    },
}

# LLM models are too large for auto-download — provide instructions instead
LLM_MODELS = {
    "tinyllama": {
        "name": "TinyLlama 1.1B Chat (Q4_K_M)",
        "size": "~670MB",
        "dest": "models/llm/tinyllama-1.1b-chat.Q4_K_M.gguf",
    },
    "phi3-mini": {
        "name": "Phi-3 Mini (Q4_K_M)",
        "size": "~2.3GB",
        "dest": "models/llm/phi-3-mini.Q4_K_M.gguf",
    },
}


def download_vosk_model(base_dir: str, force: bool = False) -> bool:
    """Download the Vosk speech model.

    Args:
        base_dir: Project base directory.
        force: Re-download even if model exists.

    Returns:
        True if model is ready to use.
    """
    model_info = MODELS["vosk"]
    dest = os.path.join(base_dir, model_info["dest"])

    if os.path.isdir(dest) and not force:
        print(f"  Vosk model already exists at {dest}")
        return True

    print(f"  Downloading Vosk model ({model_info['size']})...")
    zip_path = os.path.join(base_dir, "models", "vosk-model.zip")

    try:
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)

        # Download with progress
        def _progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(downloaded / total_size * 100, 100)
                sys.stdout.write(f"\r  Progress: {percent:.1f}%")
                sys.stdout.flush()

        urllib.request.urlretrieve(model_info["url"], zip_path, _progress)
        print()

        # Extract
        print("  Extracting...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(os.path.join(base_dir, "models"))

        # Clean up zip
        os.remove(zip_path)
        print(f"  Vosk model ready at {dest}")
        return True

    except Exception as e:
        print(f"  Download failed: {e}")
        return False


def print_llm_instructions():
    """Print instructions for downloading LLM models."""
    print("\n  LLM Model Setup")
    print("  " + "─" * 40)
    print("  SOL can use a local LLM for smarter conversations.")
    print("  Download a GGUF model and place it in models/llm/\n")

    for key, info in LLM_MODELS.items():
        print(f"  {info['name']} ({info['size']})")
        print(f"    Save to: {info['dest']}")
        print()

    print("  Then set brain.backend = 'llm' in sol.toml")
    print("  " + "─" * 40)


def check_models(base_dir: str) -> dict:
    """Check which models are available.

    Returns dict with model availability status.
    """
    status = {}

    # Check Vosk
    vosk_path = os.path.join(base_dir, MODELS["vosk"]["dest"])
    status["vosk"] = os.path.isdir(vosk_path)

    # Check LLM models
    for key, info in LLM_MODELS.items():
        path = os.path.join(base_dir, info["dest"])
        status[f"llm_{key}"] = os.path.isfile(path)

    status["has_any_llm"] = any(v for k, v in status.items() if k.startswith("llm_"))

    return status
