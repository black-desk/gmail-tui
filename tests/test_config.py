"""Tests for Gmail TUI configuration.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest
import yaml

from gmail_tui.config.loader import get_config
from gmail_tui.config.init import init_config
from gmail_tui.config.types import Config


@pytest.fixture
def temp_config_dir() -> Generator[Path, None, None]:
    """Create a temporary configuration directory.

    Returns:
        Generator yielding a temporary directory path

    """
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
    # Create a minimal valid config
    config_dir = temp_config_dir / "gmail-tui"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"

    minimal_config = {
        "gmail": {
            "email": "test@gmail.com",
            "app_password": "test-password",
        }
    }

    with config_file.open("w") as f:
        yaml.dump(minimal_config, f)

    config = get_config()
    assert config.email == "test@gmail.com"
    assert config.app_password == "test-password"


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
        }
    }

    with config_file.open("w") as f:
        yaml.dump(user_config, f)

    # Load config
    config = get_config()
    assert config.email == "test@gmail.com"
    assert config.app_password == "test-password"


def test_init_config(temp_config_dir: Path) -> None:
    """Test configuration initialization."""
    # Initialize config with test values
    init_config(email="test@gmail.com", app_password="test-password")

    # Check if config file was created
    config_file = temp_config_dir / "gmail-tui" / "config.yaml"
    assert config_file.exists()

    # Load and verify config
    with config_file.open() as f:
        config = yaml.safe_load(f)
        assert "gmail" in config
        assert config["gmail"]["email"] == "test@gmail.com"
        assert config["gmail"]["app_password"] == "test-password"


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
        }
    }

    with config_file.open("w") as f:
        yaml.dump(existing_config, f)

    # Initialize config
    init_config(email="new@gmail.com", app_password="new-password")

    # Verify config was not changed
    with config_file.open() as f:
        config = yaml.safe_load(f)
        assert config["gmail"]["email"] == "test@gmail.com"
        assert config["gmail"]["app_password"] == "test-password"


def test_invalid_config_format() -> None:
    """Test handling of invalid configuration format."""
    with pytest.raises(ValueError, match="Configuration must be a dictionary"):
        Config([])  # type: ignore


def test_missing_gmail_config() -> None:
    """Test handling of missing Gmail configuration."""
    with pytest.raises(ValueError, match="Gmail configuration not found"):
        Config({})


def test_invalid_gmail_credentials() -> None:
    """Test handling of invalid Gmail credentials."""
    with pytest.raises(SystemExit):
        Config({"gmail": {"email": "", "app_password": ""}})
    with pytest.raises(SystemExit):
        Config({"gmail": {"email": "test@gmail.com", "app_password": ""}})


def test_cli_init_command(temp_config_dir: Path) -> None:
    """Test CLI init command."""
    # Save original sys.argv
    original_argv = sys.argv

    try:
        # Test command line initialization
        sys.argv = [
            "gmail-tui",
            "init",
            "--email",
            "test@gmail.com",
            "--app-password",
            "test-password",
        ]
        from gmail_tui import main
        main()

        # Verify config was created
        config_file = temp_config_dir / "gmail-tui" / "config.yaml"
        assert config_file.exists()

        # Verify config content
        with config_file.open() as f:
            config = yaml.safe_load(f)
            assert config["gmail"]["email"] == "test@gmail.com"
            assert config["gmail"]["app_password"] == "test-password"

    finally:
        # Restore original sys.argv
        sys.argv = original_argv