"""Configuration loader for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import yaml
from xdg import XDG_CONFIG_HOME, XDG_CONFIG_DIRS
from pathlib import Path
from typing import Any

from .default import DEFAULT_CONFIG
from .actions import ACTIONS


def load_config() -> dict[str, Any]:
    """Load configuration from XDG config directories."""
    config = yaml.safe_load(DEFAULT_CONFIG)
    config_dirs = [XDG_CONFIG_HOME / "gmail-tui"] + [
        Path(d) / "gmail-tui" for d in XDG_CONFIG_DIRS
    ]

    for config_dir in config_dirs:
        config_file = config_dir / "config.yaml"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    user_config = yaml.safe_load(f)
                    if user_config and "bindings" in user_config:
                        config["bindings"] = user_config["bindings"]
            except (yaml.YAMLError, OSError):
                continue

    # 添加动作描述
    for binding in config["bindings"]:
        action = binding["action"]
        if action in ACTIONS:
            binding["description"] = ACTIONS[action]["description"]

    return config 