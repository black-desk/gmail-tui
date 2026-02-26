"""Test configuration and fixtures.

SPDX-FileCopyrightText: 2024-2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Fixtures directory containing test data
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_config():
    """Return a mock configuration for testing.

    Returns:
        MagicMock: A mock configuration object with test values

    """
    config = MagicMock()
    config.email = "test@example.com"
    config.app_password = "test_password"  # noqa: S105
    return config


@pytest.fixture
def test_config_env():
    """Fixture to check if test config is available.

    Returns:
        Path: Path to test config file if GMAIL_TUI_CONFIG is set, None otherwise

    """
    config_path = os.getenv("GMAIL_TUI_CONFIG")
    return Path(config_path) if config_path else None


def _is_test_server_running() -> bool:
    """Check if test IMAP server is running.

    Returns:
        bool: True if server is running

    """
    import socket

    from gmail_tui.config import get_config

    config = get_config()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(("127.0.0.1", config.imap_port))
        sock.close()
        return result == 0
    except OSError:
        return False


@pytest.fixture
def smtp4dev_server():
    """Fixture to check if test server is running.

    Yields:
        dict: Server configuration if running, None otherwise

    """
    from gmail_tui.config import get_config

    if _is_test_server_running():
        config = get_config()
        yield {"host": "127.0.0.1", "port": config.imap_port}
    else:
        pytest.skip("Test server not running - run ./scripts/run_e2e_tests.sh first")
