"""Rm command for Gmail TUI.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import argparse
import sys

from gmail_tui.commands.base import Command
from gmail_tui.config import get_config
from gmail_tui.utils import delete_folder, get_imap_connection


class RmCommand(Command):
    """Command for deleting email folders."""

    @property
    def name(self) -> str:
        """Get the command name."""
        return "rm"

    @property
    def help(self) -> str:
        """Get the command help text."""
        return "Delete a folder"

    def add_parser(self, subparsers: argparse._SubParsersAction) -> None:
        """Add command parser to subparsers.

        Args:
            subparsers: The subparsers object from ArgumentParser

        """
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument("folder", help="Folder name to delete")

    def handle(self, args: argparse.Namespace) -> None:
        """Handle the command.

        Args:
            args: The parsed arguments

        """
        config = get_config()
        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                if not delete_folder(client, args.folder):
                    sys.stderr.write("Error: Failed to delete folder\n")
                    sys.exit(1)
        except Exception as e:
            sys.stderr.write(f"Error: {e!s}\n")
            sys.exit(1)
