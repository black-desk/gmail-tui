"""Test configuration and fixtures.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import pytest
from unittest.mock import MagicMock

# Mock configuration for tests
@pytest.fixture
def mock_config():
    config = MagicMock()
    config.email = "test@example.com"
    config.app_password = "test_password"
    return config

# Mock IMAPClient for tests
@pytest.fixture
def mock_imap_client():
    client = MagicMock()
    client.login.return_value = b'OK'
    client.logout.return_value = b'OK'
    client.select_folder.return_value = {'EXISTS': 10}
    client.search.return_value = [1, 2, 3]
    return client