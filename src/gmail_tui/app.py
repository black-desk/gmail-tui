"""Main application module for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import sys
from typing import ClassVar, NoReturn

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Label

from .config.loader import load_config
from .config.types import ActionInfo, Config


def print_init_message() -> NoReturn:
    """Print initialization message and exit."""
    print("Gmail credentials not found in configuration.")
    print("Please run 'gmail-tui init' to set up your credentials.")
    sys.exit(1)


class GmailTUI(App):
    """A simple Gmail TUI application."""

    ACTIONS: ClassVar[dict[str, ActionInfo]] = {
        "quit": ActionInfo("quit", "Quit"),
    }

    def __init__(self) -> None:
        """Initialize the application."""
        # Load configuration before initializing the app
        self.config = load_config()

        # Check if credentials are configured
        if not self.config["gmail"]["email"] or not self.config["gmail"]["app_password"]:
            print_init_message()

        # Set up key bindings from configuration
        bindings = []
        for key, action_name in self.config["bindings"].items():
            if action_name in self.ACTIONS:
                action_info = self.ACTIONS[action_name]
                bindings.append(Binding(key, action_info.name, action_info.description))

        # Initialize the app with configured bindings
        super().__init__(bindings=bindings)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Label("Hello World")
        yield Footer()


def main() -> None:
    """Run the application."""
    app = GmailTUI()
    app.run()


if __name__ == "__main__":
    main()
