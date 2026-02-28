"""Threads command for Gmail TUI.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import argparse

from gmail_tui.commands.base import Command
from gmail_tui.threads import list_threads


class ThreadsCommand(Command):
    """Command for listing email threads."""

    @property
    def name(self) -> str:
        """Get the command name."""
        return "threads"

    @property
    def help(self) -> str:
        """Get the command help text."""
        return "List threads (grouped by conversation)"

    def add_parser(self, subparsers: argparse._SubParsersAction) -> None:
        """Add command parser to subparsers.

        Args:
            subparsers: The subparsers object from ArgumentParser

        """
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument(
            "folder",
            nargs="?",
            default="INBOX",
            help="Folder to list threads from (default: INBOX)",
        )
        parser.add_argument(
            "--limit",
            "-l",
            type=int,
            help="Maximum number of threads to show",
            default=20,
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
        list_threads(args.folder, args.limit, args.format)
