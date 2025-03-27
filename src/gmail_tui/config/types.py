"""Configuration types for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import sys
from typing import TypedDict


class GmailConfig(TypedDict):
    """Gmail configuration."""

    email: str
    app_password: str


class Config(TypedDict):
    """Application configuration."""

    gmail: GmailConfig
    bindings: dict[str, str]

    def __init__(self, data: dict) -> None:
        """Initialize configuration from data.

        Args:
            data: Configuration data dictionary

        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a dictionary")

        if "gmail" not in data or not isinstance(data["gmail"], dict):
            raise ValueError("Configuration must contain 'gmail' section")

        if "bindings" not in data or not isinstance(data["bindings"], dict):
            raise ValueError("Configuration must contain 'bindings' section")

        # Check Gmail credentials
        gmail_config = data["gmail"]
        if not isinstance(gmail_config.get("email"), str) or not gmail_config["email"]:
            print("Gmail credentials not found in configuration.")
            print("Please run 'gmail-tui init' to set up your credentials.")
            sys.exit(1)

        if not isinstance(gmail_config.get("app_password"), str) or not gmail_config["app_password"]:
            print("Gmail credentials not found in configuration.")
            print("Please run 'gmail-tui init' to set up your credentials.")
            sys.exit(1)

        # Update self with validated data
        self.update(data)


class ActionInfo(NamedTuple):
    """Action information."""

    name: str
    description: str 