"""Main application module for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Label

from .config.loader import load_config
from .config.actions import Action, ACTION_DESCRIPTIONS


class GmailTUI(App):
    """A simple Gmail TUI application."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Label("Hello World")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the application on mount."""
        config = load_config()
        for key, action_name in config["bindings"].items():
            try:
                action = Action(action_name)
                self.bind(key, action.value, ACTION_DESCRIPTIONS[action])
            except ValueError:
                continue  # 忽略无效的动作名称


def main() -> None:
    """Run the application."""
    app = GmailTUI()
    app.run()


if __name__ == "__main__":
    main()
