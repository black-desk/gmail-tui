"""Gmail TUI application.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black_desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from typing import ClassVar

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Footer, Header

from gmail_tui.config import get_config
from gmail_tui.utils import close_all_imap_connections
from gmail_tui.widgets.email_list import EmailList
from gmail_tui.widgets.folder_tree import FolderTree


class GmailTUI(App):
    """Gmail TUI application."""

    TITLE = "Gmail TUI"
    CSS = """
    #folder-tree {
        width: 30%;
        height: 100%;
        border-right: solid $primary;
    }

    #email-list {
        width: 70%;
        height: 100%;
    }
    """

    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self) -> None:
        """Initialize the application."""
        super().__init__()
        self.folder_tree = FolderTree()
        self.email_list = EmailList()

    def on_mount(self) -> None:
        """Handle application mount."""
        # Get configuration
        config = get_config()

        # Set credentials
        self.folder_tree.set_credentials(
            email=config.email, app_password=config.app_password
        )
        self.email_list.set_credentials(
            email=config.email, app_password=config.app_password
        )

        # Refresh folder tree
        self.folder_tree.action_refresh_directories()

        # Set default folder
        self.email_list.set_folder("INBOX")

    def compose(self) -> ComposeResult:
        """Compose the application layout.

        Returns:
            Iterator of child widgets

        """
        yield Header()
        yield Horizontal(
            Container(self.folder_tree, id="folder-tree"),
            Container(self.email_list, id="email-list"),
        )
        yield Footer()

    def on_unmount(self) -> None:
        """Handle application unmount."""
        # Close all IMAP connections when the app exits
        close_all_imap_connections()

    @on(FolderTree.FolderSelected)
    def on_folder_tree_folder_selected(
        self, message: FolderTree.FolderSelected
    ) -> None:
        """Handle folder selection.

        Args:
            message: Folder selected message

        """
        self.email_list.set_folder(message.folder)

    @work(thread=True)
    def action_refresh(self) -> None:
        """Refresh action."""
        self.folder_tree.action_refresh_directories()
        self.email_list.action_refresh()

    def action_quit(self) -> None:
        """Quit the application."""
        # Make sure to close all IMAP connections before quitting
        close_all_imap_connections()
        self.exit()


def main() -> None:
    """Run the Gmail TUI application."""
    app = GmailTUI()
    app.run()


if __name__ == "__main__":
    main()
