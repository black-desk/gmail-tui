"""Test configuration and fixtures.

SPDX-FileCopyrightText: 2024-2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import os
import socket
from pathlib import Path

import pytest

from gmail_tui.config import get_config
from gmail_tui.utils.imap import get_imap_connection

# Fixtures directory containing test data
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _is_greenmail_running() -> bool:
    """Check if GreenMail test server is running.

    Only returns True if:
    1. GMAIL_TUI_CONFIG is set (using test config)
    2. The GreenMail server is reachable

    Returns:
        bool: True if server is running and using test config

    """
    # First check if we're using test config (not production)
    test_config_path = os.getenv("GMAIL_TUI_CONFIG")
    if not test_config_path:
        return False

    # Check if the test config file exists
    if not os.path.exists(test_config_path):
        return False

    config = get_config()

    # Verify we're connecting to the test server (localhost:3143)
    if config.imap_server != "localhost" or config.imap_port != 3143:
        return False

    # Now check if the server is actually running
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex((config.imap_server, config.imap_port))
        sock.close()
        return result == 0
    except OSError:
        return False


@pytest.fixture
def greenmail_server():
    """Fixture to check if GreenMail test server is running.

    Yields:
        None: Yields None if server is running, otherwise skips test

    """
    if _is_greenmail_running():
        yield None
    else:
        pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")


@pytest.fixture
def imap_connection():
    """Provide an IMAP connection to GreenMail test server.

    Yields:
        IMAPClient: A connected IMAPClient instance

    """
    if not _is_greenmail_running():
        pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    config = get_config()
    with get_imap_connection(username=config.email, password=config.app_password) as client:
        yield client
