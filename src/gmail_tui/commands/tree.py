"""Tree command for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import argparse
import sys

from gmail_tui.commands.base import Command
from gmail_tui.config import get_config
from gmail_tui.imap_tree import IMAPTree
from gmail_tui.utils import connect_imap


class TreeCommand(Command):
    """Command for displaying email folders in tree format."""

    @property
    def name(self) -> str:
        """Get the command name."""
        return "tree"

    @property
    def help(self) -> str:
        """Get the command help text."""
        return "Display email folders in tree format"

    def add_parser(self, subparsers: argparse._SubParsersAction) -> None:
        """Add command parser to subparsers.

        Args:
            subparsers: The subparsers object from ArgumentParser

        """
        subparsers.add_parser(self.name, help=self.help)

    def handle(self, args: argparse.Namespace) -> None:
        """Handle the command.

        Args:
            args: The parsed arguments

        """
        config = get_config()
        try:
            with connect_imap(
                username=config.email, password=config.app_password
            ) as client:
                folders = client.list_folders()
                if not folders:
                    print("No folders found")
                    return

                tree = IMAPTree(folders)
                tree.print_tree()
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
