"""Main application module for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Label


class GmailTUI(App):
    """A simple Gmail TUI application."""

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("q", "quit", "Quit", show=True),
    ]

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
