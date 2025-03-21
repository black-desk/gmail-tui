"""Configuration types.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import logging
import sys
from typing import NamedTuple


class Config:
    """Configuration class."""

    def __init__(self, data: dict) -> None:
        """Initialize configuration.

        Args:
            data: Configuration data dictionary

        Raises:
            ValueError: If configuration is invalid

        """
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a dictionary")

        # Validate Gmail configuration
        if "gmail" not in data:
            raise ValueError("Gmail configuration not found")

        gmail_config = data["gmail"]
        if not isinstance(gmail_config.get("email"), str) or not gmail_config["email"]:
            logging.error("Gmail credentials not found in configuration.")
            logging.error("Please run 'gmail-tui init' to set up your credentials.")
            sys.exit(1)

        if (
            not isinstance(gmail_config.get("app_password"), str)
            or not gmail_config["app_password"]
        ):
            logging.error("Gmail credentials not found in configuration.")
            logging.error("Please run 'gmail-tui init' to set up your credentials.")
            sys.exit(1)

        self.email = gmail_config["email"]
        self.app_password = gmail_config["app_password"]
        self.bindings = data.get("bindings", {})


class ActionInfo(NamedTuple):
    """Action information."""

    name: str
    description: str
    default_binding: str
