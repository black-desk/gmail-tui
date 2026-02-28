"""Show command for Gmail TUI.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import argparse

from gmail_tui.commands.base import Command
from gmail_tui.show import show_email


class ShowCommand(Command):
    """Command for displaying full email content."""

    @property
    def name(self) -> str:
        """Get the command name."""
        return "show"

    @property
    def help(self) -> str:
        """Get the command help text."""
        return "Display full email content (supports uid or message-id)"

    def add_parser(self, subparsers: argparse._SubParsersAction) -> None:
        """Add command parser to subparsers.

        Args:
            subparsers: The subparsers object from ArgumentParser

        """
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument(
            "id",
            help="Email identifier: uid (number) or message-id (e.g. <xxx@example.com>)",
        )
        parser.add_argument(
            "--folder",
            "-F",
            default="INBOX",
            help="Folder containing the email (default: INBOX)",
        )
        parser.add_argument(
            "--format",
            "-f",
            help="Output format (json/yaml/toml/raw)",
            default="raw",
            choices=["json", "yaml", "toml", "raw"],
        )
        parser.add_argument(
            "--include-headers",
            action="store_true",
            help="Show all email headers",
        )

    def handle(self, args: argparse.Namespace) -> None:
        """Handle the command.

        Args:
            args: The parsed arguments

        """
        show_email(args.id, args.folder, args.format, args.include_headers)
