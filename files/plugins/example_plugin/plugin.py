"""Example SOL Plugin — demonstrates how to extend SOL with custom behaviors."""

from sol.plugins.base_plugin import BasePlugin


class ExamplePlugin(BasePlugin):
    """A simple example plugin that responds to a custom command."""

    @property
    def name(self):
        return "example"

    @property
    def version(self):
        return "1.0.0"

    @property
    def description(self):
        return "Example plugin showing how to extend SOL"

    def on_user_input(self, text):
        # Handle the /hello command
        if text.strip().lower() == "/hello":
            return "SOL plugin say hello! Plugin is working. Amaze!"

        # Handle coin flip
        if "flip a coin" in text.lower():
            import random
            result = random.choice(["heads", "tails"])
            return f"SOL flip coin... {result}! SOL like games."

        # Return None to let the brain handle it normally
        return None

    def on_session_start(self):
        self.ctx.display("Example plugin loaded!", "dim")

    def get_commands(self):
        return {
            "/hello": lambda: "SOL plugin say hello!",
        }
