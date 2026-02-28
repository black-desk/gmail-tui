"""Search command for Gmail TUI.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import argparse

from gmail_tui.commands.base import Command
from gmail_tui.search import search_emails


class SearchCommand(Command):
    """Command for searching emails."""

    @property
    def name(self) -> str:
        """Get the command name."""
        return "search"

    @property
    def help(self) -> str:
        """Get the command help text."""
        return "Search emails by sender/subject/content"

    def add_parser(self, subparsers: argparse._SubParsersAction) -> None:
        """Add command parser to subparsers.

        Args:
            subparsers: The subparsers object from ArgumentParser

        """
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument(
            "query",
            nargs="?",
            default="",
            help="Search query (use --from, --to, --subject, --body for specific filters)",
        )
        parser.add_argument(
            "--from",
            "-F",
            dest="from_addr",
            help="Filter by sender email address",
        )
        parser.add_argument(
            "--to",
            "-T",
            dest="to_addr",
            help="Filter by recipient email address",
        )
        parser.add_argument(
            "--subject",
            "-S",
            help="Filter by subject text",
        )
        parser.add_argument(
            "--body",
            "-B",
            help="Search in email body (slower, requires fetching content)",
        )
        parser.add_argument(
            "--folder",
            "-f",
            default="INBOX",
            help="Folder to search in (default: INBOX)",
        )
        parser.add_argument(
            "--limit",
            "-l",
            type=int,
            help="Maximum number of results to show",
            default=20,
        )
        parser.add_argument(
            "--format",
            "-o",
            help="Output format (json/yaml/toml)",
            default="json",
            choices=["json", "yaml", "toml"],
        )

    def handle(self, args: argparse.Namespace) -> None:
        """Handle the command.

        Args:
            args: The parsed arguments

        """
        search_emails(
            folder=args.folder,
            limit=args.limit,
            output_format=args.format,
            from_addr=args.from_addr,
            to_addr=args.to_addr,
            subject=args.subject,
            body=args.body,
        )
