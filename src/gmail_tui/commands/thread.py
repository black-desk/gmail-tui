"""Thread command for Gmail TUI.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import argparse

from gmail_tui.commands.base import Command
from gmail_tui.thread import show_thread


class ThreadCommand(Command):
    """Command for displaying all emails in a thread."""

    @property
    def name(self) -> str:
        """Get the command name."""
        return "thread"

    @property
    def help(self) -> str:
        """Get the command help text."""
        return "Display all emails in a thread (any message-id in the thread)"

    def add_parser(self, subparsers: argparse._SubParsersAction) -> None:
        """Add command parser to subparsers.

        Args:
            subparsers: The subparsers object from ArgumentParser

        """
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument(
            "message_id",
            help="Any message ID from the thread (e.g. <xxx@example.com>)",
        )
        parser.add_argument(
            "--folder",
            "-F",
            default="INBOX",
            help="Folder to search in (default: INBOX)",
        )
        parser.add_argument(
            "--format",
            "-f",
            help="Output format (json/yaml/toml)",
            default="json",
            choices=["json", "yaml", "toml"],
        )

    def handle(self, args: argparse.Namespace) -> None:
        """Handle the command.

        Args:
            args: The parsed arguments

        """
        show_thread(args.message_id, args.folder, args.format)
