"""Tests for the plugin system."""

import os
import pytest
from sol.plugins.base_plugin import BasePlugin, PluginContext
from sol.plugins.hooks import run_on_user_input, run_on_response


class MockPlugin(BasePlugin):
    @property
    def name(self):
        return "mock"

    def on_user_input(self, text):
        if text == "magic word":
            return "Plugin handled this!"
        return None

    def on_response(self, user_input, response):
        return response + " (plugin was here)"


class TestPluginSystem:

    def test_plugin_on_user_input_override(self):
        plugin = MockPlugin()
        result = run_on_user_input([plugin], "magic word")
        assert result == "Plugin handled this!"

    def test_plugin_on_user_input_passthrough(self):
        plugin = MockPlugin()
        result = run_on_user_input([plugin], "normal text")
        assert result is None

    def test_plugin_on_response_modification(self):
        plugin = MockPlugin()
        result = run_on_response([plugin], "hello", "SOL says hi")
        assert "(plugin was here)" in result

    def test_empty_plugin_list(self):
        result = run_on_user_input([], "hello")
        assert result is None

        result = run_on_response([], "hello", "response")
        assert result == "response"

    def test_plugin_context(self, memory_db):
        ctx = PluginContext(
            memory=memory_db,
            config={"test": True},
            speak=lambda x: None,
            display=lambda x, y: None,
        )
        assert ctx.get_friend_name() is None
        memory_db.set_friend_name("Test")
        assert ctx.get_friend_name() == "Test"

    def test_broken_plugin_doesnt_crash(self):
        class BrokenPlugin(BasePlugin):
            @property
            def name(self):
                return "broken"

            def on_user_input(self, text):
                raise RuntimeError("Oops!")

        plugin = BrokenPlugin()
        # Should not raise
        result = run_on_user_input([plugin], "hello")
        assert result is None
