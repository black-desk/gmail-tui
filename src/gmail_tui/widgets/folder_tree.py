"""Folder tree widget for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from typing import ClassVar

from textual import on, work
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Tree
from textual.widgets.tree import TreeNode

from gmail_tui.config import get_config
from gmail_tui.imap_tree import IMAPTree
from gmail_tui.utils.imap import connect_imap


class FolderTree(Widget):
    """A widget that displays email folders in a tree structure."""

    DEFAULT_CSS = """
    FolderTree {
        height: 100%;
        border: round $primary;
        padding: 0 1;
    }

    Tree {
        height: 100%;
        max-width: 100%;
    }
    """

    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("r", "refresh_directories", "Refresh"),
    ]

    class FolderSelected(Message):
        """Message sent when a folder is selected."""

        def __init__(self, folder: str) -> None:
            """Initialize the message.

            Args:
                folder: Selected folder path

            """
            self.folder = folder
            super().__init__()

    class FoldersUpdated(Message):
        """Message sent when folders are updated."""

        def __init__(self, folders: list[tuple[list[bytes], bytes, bytes]]) -> None:
            """Initialize the message.

            Args:
                folders: List of IMAP folder tuples (flags, delimiter, name)

            """
            self.folders = folders
            super().__init__()

    def __init__(self) -> None:
        """Initialize the folder tree widget."""
        super().__init__()
        self.tree_widget = Tree("Folders")
        self.tree_widget.show_root = False
        self.tree_data: IMAPTree | None = None
        self.email: str = ""
        self.app_password: str = ""

        actions = {
            key: (action_name, description)
            for (key, action_name, description) in self.BINDINGS
        }

        for key, action_name in get_config().bindings.items():
            if action_name not in actions:
                continue
            (name, description) = actions[action_name]
            super().bind(key, name, description=description)

    def set_credentials(self, email: str, app_password: str) -> None:
        """Set IMAP credentials.

        Args:
            email: Gmail address
            app_password: App password for Gmail

        """
        self.email = email
        self.app_password = app_password

    def compose(self) -> ComposeResult:
        """Compose the widget's child widgets.

        Returns:
            Iterator of child widgets

        """
        self.loading = True
        yield self.tree_widget

    def update_folders(self, folders: list[tuple[list[bytes], bytes, bytes]]) -> None:
        """Update the folder tree with new folder data.

        Args:
            folders: List of IMAP folder tuples (flags, delimiter, name)

        """
        if not folders:
            return

        # Create IMAPTree instance
        self.tree_data = IMAPTree(folders)

        # Clear existing tree
        self.tree_widget.clear()

        # Build tree widget recursively
        self._build_tree_widget()

        self.loading = False

    def _build_tree_widget(
        self, root: str = "", parent: TreeNode | None = None
    ) -> None:
        """Build the tree widget structure recursively.

        Args:
            root: Current root folder path
            parent: Parent tree node

        """
        if not self.tree_data:
            return

        if parent is None:
            parent = self.tree_widget.root

        folders = sorted(self.tree_data.tree[root])
        for folder in folders:
            if root == "":
                label = folder
            else:
                label = folder.split(self.tree_data.delimiter)[-1]

            # Check if folder has children
            has_children = folder in self.tree_data.tree and bool(
                self.tree_data.tree[folder]
            )

            # Create node with folder name and full path as data
            node = parent.add(
                label, data=folder, expand=True, allow_expand=has_children
            )

            # Add children recursively
            if has_children:
                self._build_tree_widget(folder, node)

    @on(Tree.NodeSelected)
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle node selection events.

        Args:
            event: Node selection event

        """
        if event.node.data is None:
            return

        # Post folder selected message with full folder path
        self.post_message(self.FolderSelected(str(event.node.data)))

    @on(FoldersUpdated)
    def on_folders_updated(self, message: FoldersUpdated) -> None:
        """Handle folders updated message.

        Args:
            message: Folders updated message

        """
        self.update_folders(message.folders)

    @work(thread=True)
    def action_refresh_directories(self) -> None:
        """Refresh email directories action."""
        if not self.email or not self.app_password:
            return

        # Connect to IMAP server - connection will be reused from pool if available
        client = connect_imap(username=self.email, password=self.app_password)

        try:
            # Get folder list
            folders = client.list_folders()

            # Post update message
            self.post_message(self.FoldersUpdated(folders))
        except Exception:
            # No need to close the connection as it's managed by the connection pool
            raise

    def on_mount(self) -> None:
        """Handle widget mount event."""
        # If we have credentials, refresh folders
        if self.email and self.app_password:
            self.action_refresh_directories()
