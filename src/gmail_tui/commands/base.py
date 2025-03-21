"""Base command class for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import argparse
from abc import ABC, abstractmethod


class Command(ABC):
    """Base class for all commands."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the command name."""
        pass

    @property
    @abstractmethod
    def help(self) -> str:
        """Get the command help text."""
        pass

    @abstractmethod
    def add_parser(self, subparsers: argparse._SubParsersAction) -> None:
        """Add command parser to subparsers.

        Args:
            subparsers: The subparsers object from ArgumentParser

        """
        pass

    @abstractmethod
    def handle(self, args: argparse.Namespace) -> None:
        """Handle the command.

        Args:
            args: The parsed arguments

        """
        pass
