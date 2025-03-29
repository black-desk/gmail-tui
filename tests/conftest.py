"""Test configuration and fixtures.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from unittest.mock import MagicMock

import pytest


# Mock configuration for tests
@pytest.fixture
def mock_config():
    """Return a mock configuration for testing.

    Returns:
        MagicMock: A mock configuration object with test values

    """
    config = MagicMock()
    config.email = "test@example.com"
    # Using a fixed test password for testing purposes only
    config.app_password = "test_password"  # noqa: S105
    return config


# Mock IMAPClient for tests
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
