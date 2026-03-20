"""Textual TUI — rich terminal UI for SOL."""

try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical, ScrollableContainer
    from textual.widgets import Header, Footer, Static, Input, RichLog
    from textual.reactive import reactive
    from textual import on
    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False

from sol.ui.base import UIBase
from typing import Dict, Any, Callable, Optional
import asyncio


if HAS_TEXTUAL:

    class MemorySidebar(Static):
        """Sidebar showing SOL's memory status."""

        def update_status(self, metadata: Dict[str, Any]):
            name = metadata.get("friend_name", "???")
            facts = metadata.get("facts_count", 0)
            prefs = metadata.get("prefs_count", 0)
            convos = metadata.get("conversations", 0)
            mood = metadata.get("current_mood", "---")
            depth = metadata.get("relationship_depth", 0.0)

            self.update(
                f"[bold green]Memory[/]\n"
                f"{'─' * 14}\n"
                f"Name:  [cyan]{name}[/]\n"
                f"Facts: [yellow]{facts}[/]\n"
                f"Prefs: [yellow]{prefs}[/]\n"
                f"Chats: [yellow]{convos}[/]\n"
                f"Mood:  [magenta]{mood}[/]\n"
                f"Depth: [blue]{depth:.2f}[/]\n"
            )

    class SolTuiApp(App):
        """SOL's Textual TUI application."""

        CSS = """
        Screen {
            layout: horizontal;
        }

        #chat-area {
            width: 3fr;
            height: 100%;
        }

        #chat-log {
            height: 1fr;
            border: solid green;
            scrollbar-color: green;
        }

        #input-box {
            dock: bottom;
            height: 3;
            border: solid cyan;
        }

        #sidebar {
            width: 18;
            height: 100%;
            border: solid $accent;
            padding: 1;
        }
        """

        TITLE = "SOL v2.0 — Your Local AI Friend"
        BINDINGS = [("ctrl+q", "quit", "Quit")]

        def __init__(self, on_input: Callable = None):
            super().__init__()
            self._on_input = on_input
            self._message_queue = asyncio.Queue()
            self._input_future: Optional[asyncio.Future] = None

        def compose(self) -> ComposeResult:
            yield Header()
            with Horizontal():
                with Vertical(id="chat-area"):
                    yield RichLog(id="chat-log", highlight=True, markup=True, wrap=True)
                    yield Input(placeholder="Type here or speak...", id="input-box")
                yield MemorySidebar(id="sidebar")
            yield Footer()

        def on_mount(self):
            self.query_one("#input-box", Input).focus()

        @on(Input.Submitted, "#input-box")
        def handle_input(self, event: Input.Submitted):
            text = event.value.strip()
            if text and self._input_future and not self._input_future.done():
                self._input_future.set_result(text)
            event.input.value = ""

        def add_message(self, text: str, style: str = "sol"):
            log = self.query_one("#chat-log", RichLog)
            if style == "sol":
                log.write(f"[bold green]SOL >[/] [green]{text}[/]")
            elif style == "you":
                log.write(f"[bold cyan]YOU >[/] [cyan]{text}[/]")
            elif style == "system":
                log.write(f"[bold yellow]SYS >[/] [yellow]{text}[/]")
            elif style == "dim":
                log.write(f"[dim]{text}[/]")
            elif style == "error":
                log.write(f"[bold red]ERR >[/] [red]{text}[/]")
            else:
                log.write(text)

        def update_sidebar(self, metadata: Dict[str, Any]):
            sidebar = self.query_one("#sidebar", MemorySidebar)
            sidebar.update_status(metadata)

        async def get_input_async(self) -> str:
            self._input_future = asyncio.get_event_loop().create_future()
            text = await self._input_future
            return text


class TuiUI(UIBase):
    """Textual TUI-based UI for SOL."""

    def __init__(self):
        if not HAS_TEXTUAL:
            raise ImportError("textual is not installed")
        self.app = SolTuiApp()
        self._messages = []

    def display_message(self, text: str, style: str = "sol") -> None:
        self._messages.append((text, style))
        if self.app.is_running:
            self.app.call_from_thread(self.app.add_message, text, style)

    def display_banner(self) -> None:
        self.display_message("SOL v2.0 — Your Local AI Friend", "system")
        self.display_message("No internet. No cloud. Just SOL and you.", "dim")

    def display_status(self, metadata: Dict[str, Any]) -> None:
        if self.app.is_running:
            self.app.call_from_thread(self.app.update_sidebar, metadata)

    def get_text_input(self, prompt: str = "") -> str:
        # In TUI mode, input comes through the Input widget
        # This is a synchronous fallback
        try:
            return input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            return "goodbye"

    def clear(self) -> None:
        pass
