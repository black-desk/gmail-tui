"""Test configuration and fixtures.

SPDX-FileCopyrightText: 2024-2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import os
import shutil
from collections.abc import Generator
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
def mock_imap_client():
    """Return a mock IMAP client for testing.

    Returns:
        MagicMock: A mock IMAP client with predefined return values

    """
    client = MagicMock()
    client.login.return_value = b"OK"
    client.logout.return_value = b"OK"
    client.select_folder.return_value = {"EXISTS": 10}
    client.search.return_value = [1, 2, 3]
    return client


@pytest.fixture
def test_config_env():
    """Fixture to check if test config is available.

    Returns:
        Path: Path to test config file if GMAIL_TUI_CONFIG is set, None otherwise

    """
    config_path = os.getenv("GMAIL_TUI_CONFIG")
    return Path(config_path) if config_path else None


def _is_test_server_running() -> bool:
    """Check if test IMAP server is running on localhost:143.

    Returns:
        bool: True if server is running

    """
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(("127.0.0.1", 143))
        sock.close()
        return result == 0
    except OSError:
        return False


@pytest.fixture
def smtp4dev_server():
    """Fixture to check if smtp4dev is running.

    Yields:
        dict: Server configuration if running, None otherwise

    """
    if _is_test_server_running():
        yield {"host": "127.0.0.1", "port": 143}
    else:
        pytest.skip("smtp4dev server not running - run ./scripts/run_e2e_tests.sh first")
