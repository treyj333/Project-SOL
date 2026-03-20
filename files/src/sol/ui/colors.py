"""ANSI color constants for SOL's terminal display."""


class C:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[38;5;114m"    # SOL's color — warm green
    AMBER = "\033[38;5;214m"    # amber accent
    CYAN = "\033[38;5;80m"      # input marker
    WHITE = "\033[38;5;252m"
    GRAY = "\033[38;5;240m"
    BG = "\033[48;5;234m"       # dark background
    RED = "\033[38;5;203m"
