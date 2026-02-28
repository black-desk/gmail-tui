"""Gmail TUI - A terminal user interface for Gmail.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

__version__ = "0.1.0"

import argparse

from gmail_tui.app import main as app
from gmail_tui.commands.init import InitCommand
from gmail_tui.commands.list import ListCommand
from gmail_tui.commands.mkdir import MkdirCommand
from gmail_tui.commands.mv import MvCommand
from gmail_tui.commands.rm import RmCommand
from gmail_tui.commands.show import ShowCommand
from gmail_tui.commands.tree import TreeCommand


def main() -> None:
    """Run the Gmail TUI application."""
    parser = argparse.ArgumentParser(
        description="Gmail TUI - A terminal user interface for Gmail"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register commands
    commands = [
        InitCommand(),
        ListCommand(),
        ShowCommand(),
        TreeCommand(),
        MkdirCommand(),
        RmCommand(),
        MvCommand(),
    ]

    for command in commands:
        command.add_parser(subparsers)

    args = parser.parse_args()

    if args.command:
        # Find and execute the command
        for command in commands:
            if command.name == args.command:
                command.handle(args)
                break
    else:
        app()


if __name__ == "__main__":
    main()
