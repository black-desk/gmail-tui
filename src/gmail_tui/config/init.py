"""Configuration initialization.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import logging

import yaml
from xdg import xdg_config_home

from .default import DEFAULT_CONFIG


def init_config(
    email: str | None = None,
    app_password: str | None = None,
) -> None:
    """Initialize user configuration file.

    Args:
        email: Optional Gmail address for non-interactive configuration
        app_password: Optional app password for non-interactive configuration

    """
    config_dir = xdg_config_home() / "gmail-tui"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.yaml"

    # Check if config file already exists
    if config_file.exists():
        logging.info("Configuration file already exists at %s", config_file)
        return

    # Get user input if not provided
    if email is None or app_password is None:
        logging.info("Welcome to Gmail TUI configuration!")
        logging.info("Please enter your Gmail credentials.")
        logging.info("Note: For security reasons, you should use an App Password.")
        logging.info(
            "You can generate one at: https://myaccount.google.com/apppasswords"
        )
        logging.info("")

        email = input("Gmail address: ").strip() if email is None else email
        app_password = (
            input("App Password: ").strip() if app_password is None else app_password
        )

    # Load default configuration
    config = yaml.safe_load(DEFAULT_CONFIG)

    # Update with user credentials
    config["gmail"]["email"] = email
    config["gmail"]["app_password"] = app_password

    # Write configuration
    with config_file.open("w") as f:
        yaml.dump(config, f, default_flow_style=False)

    logging.info("Configuration saved to %s", config_file)
    logging.info("You can now start Gmail TUI with 'gmail-tui' command.")
