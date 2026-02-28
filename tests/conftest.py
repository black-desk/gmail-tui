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

    Returns:
        bool: True if server is running

    """
    config = get_config()
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
