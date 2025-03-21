"""Init command for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import argparse

from gmail_tui.commands.base import Command
from gmail_tui.config.init import init_config


class InitCommand(Command):
    """Command for initializing Gmail TUI configuration."""

    @property
    def name(self) -> str:
        """Get the command name."""
        return "init"

    @property
    def help(self) -> str:
        """Get the command help text."""
        return "Initialize Gmail TUI configuration"

    def add_parser(self, subparsers: argparse._SubParsersAction) -> None:
        """Add command parser to subparsers.

        Args:
            subparsers: The subparsers object from ArgumentParser

        """
        parser = subparsers.add_parser(self.name, help=self.help)
        parser.add_argument(
            "--email",
            help="Gmail address for non-interactive configuration",
        )
        parser.add_argument(
            "--app-password",
            help="App password for non-interactive configuration",
        )

    def handle(self, args: argparse.Namespace) -> None:
        """Handle the command.

        Args:
            args: The parsed arguments

        """
        init_config(email=args.email, app_password=args.app_password)
