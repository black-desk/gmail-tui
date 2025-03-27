"""Configuration loader for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import yaml
from xdg import XDG_CONFIG_HOME, XDG_CONFIG_DIRS
from pathlib import Path
from typing import Any, TypedDict

from .default import DEFAULT_CONFIG


class GmailConfig(TypedDict):
    """Gmail configuration."""

    email: str
    app_password: str


class Config(TypedDict):
    """Application configuration."""

    gmail: GmailConfig
    bindings: dict[str, str]


def load_config() -> Config:
    """Load configuration from XDG config directories."""
    # 首先尝试加载用户配置文件
    config_dirs = [XDG_CONFIG_HOME / "gmail-tui"] + [
        Path(d) / "gmail-tui" for d in XDG_CONFIG_DIRS
    ]

    for config_dir in config_dirs:
        config_file = config_dir / "config.yaml"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = yaml.safe_load(f)
                    if config and "gmail" in config and "bindings" in config:
                        return config
            except (yaml.YAMLError, OSError):
                continue

    # 如果没有找到有效的用户配置文件，使用默认配置
    return yaml.safe_load(DEFAULT_CONFIG) 