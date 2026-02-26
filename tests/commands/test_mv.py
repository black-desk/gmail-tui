"""Tests for the mv command.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from unittest.mock import MagicMock, patch

import pytest

from gmail_tui.commands.mv import MvCommand


@pytest.fixture
def mv_command():
    """Return a mv command instance for testing."""
    return MvCommand()


def test_mv_command_handle(mv_command, mock_config):
    """Test mv command correctly handles source and dest arguments."""
    with (
        patch("gmail_tui.commands.mv.get_config", return_value=mock_config),
        patch("gmail_tui.commands.mv.get_imap_connection") as mock_get_imap_connection,
        patch(
            "gmail_tui.commands.mv.rename_folder", return_value=True
        ) as mock_rename_folder,
    ):
        mock_conn = MagicMock()
        mock_get_imap_connection.return_value.__enter__.return_value = mock_conn

        args = MagicMock()
        args.source = "OldFolder"
        args.dest = "NewFolder"
        mv_command.handle(args)

        mock_get_imap_connection.assert_called_once_with(
            username=mock_config.email, password=mock_config.app_password
        )
        mock_rename_folder.assert_called_once()


def test_mv_connection_error(mv_command, mock_config):
    """Test mv command handles connection errors."""
    with (
        patch("gmail_tui.commands.mv.get_config", return_value=mock_config),
        patch("gmail_tui.commands.mv.get_imap_connection") as mock_get_imap_connection,
        patch("sys.stderr.write") as mock_stderr_write,
        patch("sys.exit") as mock_exit,
    ):
        mock_get_imap_connection.side_effect = Exception("Connection error")

        args = MagicMock()
        args.source = "OldFolder"
        args.dest = "NewFolder"
        mv_command.handle(args)

        mock_stderr_write.assert_called_once_with("Error: Connection error\n")
        mock_exit.assert_called_once_with(1)
