"""Tests for the list command.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from unittest.mock import MagicMock, patch

import pytest

from gmail_tui.commands.list import ListCommand


@pytest.fixture
def list_command():
    """Return a ListCommand instance for testing."""
    return ListCommand()


@pytest.mark.parametrize(
    "folder, limit, format_name",
    [
        ("INBOX", 10, "json"),
        ("Sent", 5, "yaml"),
        ("[Gmail]/All Mail", 20, "toml"),
    ],
)
def test_list_command_handle(folder, limit, format_name):
    """Test if list command handle method correctly processes arguments."""
    list_command = ListCommand()

    args = MagicMock()
    args.folder = folder
    args.limit = limit
    args.format = format_name

    with patch("gmail_tui.commands.list.list_emails") as mock_list_emails:
        list_command.handle(args)
        mock_list_emails.assert_called_once_with(folder, limit, format_name)


def test_list_emails_connection_error(mock_config):
    """Test error handling for connection issues."""
    from gmail_tui.list import list_emails

    with (
        patch("gmail_tui.list.get_config", return_value=mock_config),
        patch("gmail_tui.list.get_imap_connection") as mock_get_imap_connection,
        patch("sys.stderr.write") as mock_stderr_write,
    ):
        mock_get_imap_connection.side_effect = Exception("Connection error")
        list_emails("INBOX")
        mock_stderr_write.assert_called_once_with("Error: Connection error\n")
