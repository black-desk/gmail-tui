"""Tests for Gmail TUI configuration.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
import yaml

from gmail_tui.config.loader import load_config
from gmail_tui.config.init import init_config


@pytest.fixture
def temp_config_dir() -> Generator[Path, None, None]:
    """Create a temporary configuration directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        # Save original environment variable
        original_xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        # Set test configuration directory
        os.environ["XDG_CONFIG_HOME"] = str(temp_path)
        yield temp_path
        # Restore original environment variable
        if original_xdg_config_home is None:
            os.environ.pop("XDG_CONFIG_HOME", None)
        else:
            os.environ["XDG_CONFIG_HOME"] = original_xdg_config_home


def test_load_default_config(temp_config_dir: Path) -> None:
    """Test loading default configuration."""
    config = load_config()
    assert "gmail" in config
    assert "bindings" in config
    assert config["gmail"]["email"] == ""
    assert config["gmail"]["app_password"] == ""
    assert "quit" in config["bindings"]


def test_load_user_config(temp_config_dir: Path) -> None:
    """Test loading user configuration."""
    # Create user config directory
    config_dir = temp_config_dir / "gmail-tui"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"

    # Create user config
    user_config = {
        "gmail": {
            "email": "test@gmail.com",
            "app_password": "test-password",
        },
        "bindings": {
            "q": "quit",
            "r": "refresh",
        },
    }

    with open(config_file, "w") as f:
        yaml.dump(user_config, f)

    # Load config
    config = load_config()
    assert config["gmail"]["email"] == "test@gmail.com"
    assert config["gmail"]["app_password"] == "test-password"
    assert config["bindings"]["q"] == "quit"
    assert config["bindings"]["r"] == "refresh"


def test_init_config(temp_config_dir: Path) -> None:
    """Test configuration initialization."""
    # Initialize config
    init_config()

    # Check if config file was created
    config_file = temp_config_dir / "gmail-tui" / "config.yaml"
    assert config_file.exists()

    # Load and verify config
    with open(config_file) as f:
        config = yaml.safe_load(f)
        assert "gmail" in config
        assert "bindings" in config
        assert config["gmail"]["email"] == ""
        assert config["gmail"]["app_password"] == ""
        assert "quit" in config["bindings"]


def test_init_config_existing(temp_config_dir: Path) -> None:
    """Test configuration initialization with existing config."""
    # Create existing config
    config_dir = temp_config_dir / "gmail-tui"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"

    existing_config = {
        "gmail": {
            "email": "test@gmail.com",
            "app_password": "test-password",
        },
        "bindings": {
            "q": "quit",
        },
    }

    with open(config_file, "w") as f:
        yaml.dump(existing_config, f)

    # Initialize config
    init_config()

    # Verify config was not changed
    with open(config_file) as f:
        config = yaml.safe_load(f)
        assert config["gmail"]["email"] == "test@gmail.com"
        assert config["gmail"]["app_password"] == "test-password"
        assert config["bindings"]["q"] == "quit" 