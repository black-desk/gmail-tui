"""Configuration loader for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import yaml
from xdg import xdg_config_home, xdg_config_dirs
from pathlib import Path
from typing import Any

from .default import DEFAULT_CONFIG
from .types import Config


def load_config() -> Config:
    """Load configuration from XDG config directories."""
    # First try to load user configuration file
    config_dirs = [Path(xdg_config_home()) / "gmail-tui"] + [
        Path(d) / "gmail-tui" for d in xdg_config_dirs()
    ]

    for config_dir in config_dirs:
        config_file = config_dir / "config.yaml"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config_data = yaml.safe_load(f)
                    if config_data:
                        return Config(config_data)
            except (yaml.YAMLError, OSError):
                continue

    # If no valid user configuration is found, use default configuration
    return Config(yaml.safe_load(DEFAULT_CONFIG)) 