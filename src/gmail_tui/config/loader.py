"""Configuration loader.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import logging
from typing import Optional

import yaml
from xdg import xdg_config_dirs, xdg_config_home

from .default import DEFAULT_CONFIG
from .types import Config

_config: Optional[Config] = None


def get_config() -> Config:
    """Load configuration from user config file or use default.

    Returns:
        Config: Configuration object

    """
    if _config is not None:
        return _config

    for config_dir in [xdg_config_home(), *xdg_config_dirs()]:
        config_file = config_dir / "gmail-tui" / "config.yaml"
        if config_file.exists():
            try:
                with config_file.open() as f:
                    config_data = yaml.safe_load(f)
                    if config_data:
                        return Config(config_data)
            except Exception as e:
                logging.warning("Failed to load config from %s: %s", config_file, e)
                continue

    # If no valid user configuration is found, use default configuration
    return Config(yaml.safe_load(DEFAULT_CONFIG))
