"""Tests for the mkdir command.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from unittest.mock import MagicMock, patch

import pytest

from gmail_tui.commands.mkdir import MkdirCommand


@pytest.fixture
def mkdir_command():
    """Return a mkdir command instance for testing."""
    return MkdirCommand()


def test_mkdir_command_handle(mkdir_command, mock_config):
    """Test mkdir command correctly handles folder argument."""
    with (
        patch("gmail_tui.commands.mkdir.get_config", return_value=mock_config),
        patch(
            "gmail_tui.commands.mkdir.get_imap_connection"
        ) as mock_get_imap_connection,
        patch(
            "gmail_tui.commands.mkdir.create_folder", return_value=True
        ) as mock_create_folder,
    ):
        mock_conn = MagicMock()
        mock_get_imap_connection.return_value.__enter__.return_value = mock_conn

        args = MagicMock()
        args.folder = "TestFolder"
        mkdir_command.handle(args)

        mock_get_imap_connection.assert_called_once_with(
            username=mock_config.email, password=mock_config.app_password
        )
        mock_create_folder.assert_called_once()


def test_mkdir_connection_error(mkdir_command, mock_config):
    """Test mkdir command handles connection errors."""
    with (
        patch("gmail_tui.commands.mkdir.get_config", return_value=mock_config),
        patch(
            "gmail_tui.commands.mkdir.get_imap_connection"
        ) as mock_get_imap_connection,
        patch("sys.stderr.write") as mock_stderr_write,
        patch("sys.exit") as mock_exit,
    ):
        mock_get_imap_connection.side_effect = Exception("Connection error")

        args = MagicMock()
        args.folder = "TestFolder"
        mkdir_command.handle(args)

        mock_stderr_write.assert_called_once_with("Error: Connection error\n")
        mock_exit.assert_called_once_with(1)
