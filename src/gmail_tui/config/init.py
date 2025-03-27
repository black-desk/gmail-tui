"""Configuration initialization for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import os
import yaml
from pathlib import Path
from typing import Optional
from xdg import xdg_config_home

from .default import DEFAULT_CONFIG


def init_config(email: Optional[str] = None, app_password: Optional[str] = None) -> None:
    """Initialize user configuration file.

    Args:
        email: Optional Gmail address for non-interactive configuration
        app_password: Optional app password for non-interactive configuration
    """
    # Get config directory
    config_dir = Path(xdg_config_home()) / "gmail-tui"
    config_file = config_dir / "config.yaml"

    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    # Check if config file already exists
    if config_file.exists():
        print(f"Configuration file already exists at {config_file}")
        return

    # Get user input if not provided
    if email is None or app_password is None:
        print("Welcome to Gmail TUI configuration!")
        print("Please enter your Gmail credentials.")
        print("Note: For security reasons, you should use an App Password.")
        print("You can generate one at: https://myaccount.google.com/apppasswords")
        print()

        email = input("Gmail address: ").strip() if email is None else email
        app_password = input("App Password: ").strip() if app_password is None else app_password

    # Load default configuration
    config = yaml.safe_load(DEFAULT_CONFIG)

    # Update Gmail credentials
    config["gmail"]["email"] = email
    config["gmail"]["app_password"] = app_password

    # Write configuration
    with open(config_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"\nConfiguration saved to {config_file}")
    print("You can now start Gmail TUI with 'gmail-tui' command.") 