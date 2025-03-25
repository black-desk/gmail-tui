"""Default configuration for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from pathlib import Path
from typing import TypedDict


class KeyBinding(TypedDict):
    """Key binding configuration."""

    key: str
    action: str
    description: str


def load_default_config() -> str:
    """Load default configuration from YAML file."""
    config_path = Path(__file__).parent / "default.yaml"
    return config_path.read_text()


DEFAULT_CONFIG = load_default_config() 