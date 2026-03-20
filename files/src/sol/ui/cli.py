"""CLI terminal display — retro terminal aesthetic from SOL v1."""

import os
import sys
import time
import textwrap
from typing import Dict, Any

from sol.ui.base import UIBase
from sol.ui.colors import C


class CliUI(UIBase):
    """Terminal-based UI with ANSI colors and typewriter effect."""

    def display_message(self, text: str, style: str = "sol") -> None:
        prefix = ""
        color = C.WHITE

        if style == "sol":
            prefix = f"  {C.GREEN}{C.BOLD}SOL >{C.RESET} "
            color = C.GREEN
        elif style == "you":
            prefix = f"  {C.CYAN}YOU >{C.RESET} "
            color = C.CYAN
        elif style == "system":
            prefix = f"  {C.AMBER}SYS >{C.RESET} "
            color = C.AMBER
        elif style == "dim":
            prefix = f"  {C.GRAY}    {C.RESET} "
            color = C.GRAY
        elif style == "error":
            prefix = f"  {C.RED}ERR >{C.RESET} "
            color = C.RED

        lines = textwrap.wrap(text, width=60)
        for i, line in enumerate(lines):
            if i == 0:
                sys.stdout.write(prefix)
            else:
                # Indent continuation lines to align with first line
                sys.stdout.write("       " + " " * 2)

            # Typewriter effect for SOL's responses
            if style == "sol":
                for char in line:
                    sys.stdout.write(f"{color}{char}{C.RESET}")
                    sys.stdout.flush()
                    time.sleep(0.02)
            else:
                sys.stdout.write(f"{color}{line}{C.RESET}")

            print()

    def display_banner(self) -> None:
        self.clear()
        banner = f"""
{C.GREEN}{C.BOLD}
    ███████╗ ██████╗ ██╗
    ██╔════╝██╔═══██╗██║
    ███████╗██║   ██║██║
    ╚════██║██║   ██║██║
    ███████║╚██████╔╝███████╗
    ╚══════╝ ╚═════╝ ╚══════╝{C.RESET}

    {C.AMBER}╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌{C.RESET}
    {C.DIM}  LOCAL AI FRIEND • v2.0{C.RESET}
    {C.DIM}  No internet. No cloud.{C.RESET}
    {C.DIM}  Just SOL and you.{C.RESET}
    {C.AMBER}╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌{C.RESET}
"""
        print(banner)

    def display_status(self, metadata: Dict[str, Any]) -> None:
        name = metadata.get("friend_name", "???")
        facts = metadata.get("facts_count", 0)
        prefs = metadata.get("prefs_count", 0)
        convos = metadata.get("conversations", 0)
        depth = metadata.get("relationship_depth")
        mood = metadata.get("current_mood")

        status_parts = [f"Friend: {name}", f"Facts: {facts}", f"Prefs: {prefs}", f"Chats: {convos}"]
        if mood:
            status_parts.append(f"Mood: {mood}")
        if depth is not None:
            status_parts.append(f"Depth: {depth:.2f}")

        status_line = " │ ".join(status_parts)
        print(f"  {C.GRAY}┌─ {status_line} ─┐{C.RESET}")
        print(f"  {C.GRAY}└─ Memory grows the more you talk ──────────────────────┘{C.RESET}")
        print()

    def get_text_input(self, prompt: str = "") -> str:
        try:
            user_input = input(f"  {C.CYAN}YOU >{C.RESET} ")
            return user_input.strip()
        except (EOFError, KeyboardInterrupt):
            return "goodbye"

    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")
