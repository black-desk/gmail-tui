"""Mv command for Gmail TUI.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import argparse
import sys

from gmail_tui.commands.base import Command
from gmail_tui.config import get_config
from gmail_tui.utils import get_imap_connection, rename_folder


class MvCommand(Command):
    """Command for renaming/moving email folders."""

    @property
    def name(self) -> str:
        """Get the command name."""
        return "mv"

    @property
    def help(self) -> str:
        """Get the command help text."""
        return "Rename/move a folder"

    def add_parser(self, subparsers: argparse._SubParsersAction) -> None:
        """Add command parser to subparsers.

        Args:
            subparsers: The subparsers object from ArgumentParser

        """
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument("source", help="Source folder name")
        parser.add_argument("dest", help="Destination folder name")

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
                if not rename_folder(client, args.source, args.dest):
                    sys.stderr.write("Error: Failed to rename folder\n")
                    sys.exit(1)
        except Exception as e:
            sys.stderr.write(f"Error: {e!s}\n")
            sys.exit(1)
