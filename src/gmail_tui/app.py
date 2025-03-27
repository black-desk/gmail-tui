"""Main application module for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Label

from .config.loader import load_config
from .config.types import ActionInfo


class GmailTUI(App):
    """A simple Gmail TUI application."""

    ACTIONS: ClassVar[dict[str, ActionInfo]] = {
        "quit": ActionInfo("quit", "Quit"),
    }

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Label("Hello World")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the application on mount."""
        config = load_config()
        for key, action_name in config["bindings"].items():
            if action_name in self.ACTIONS:
                action_info = self.ACTIONS[action_name]
                self.bind(key, action_info.name, action_info.description)


def main() -> None:
    """Run the application."""
    app = GmailTUI()
    app.run()


if __name__ == "__main__":
    main()
