"""Test module for the tree command.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from unittest.mock import MagicMock, patch

import pytest

from gmail_tui.commands.tree import TreeCommand


@pytest.fixture
def tree_command():
    """Return a tree command instance for testing."""
    return TreeCommand()


def test_tree_command_handle(tree_command, mock_config, mock_imap_client):
    """Test if the tree command correctly processes folder list and outputs tree."""
    # Set up mock IMAP client response
    mock_imap_client.list_folders.return_value = [
        ([b"\\HasNoChildren"], b"/", b"INBOX"),
        ([b"\\HasNoChildren"], b"/", b"Sent"),
        ([b"\\HasNoChildren"], b"/", b"Trash"),
        ([b"\\HasChildren"], b"/", b"[Gmail]"),
        ([b"\\HasNoChildren"], b"/", b"[Gmail]/All Mail"),
        ([b"\\HasNoChildren"], b"/", b"[Gmail]/Sent Mail"),
        ([b"\\HasNoChildren"], b"/", b"[Gmail]/Trash"),
    ]

    # Mock functions
    with (
        patch("gmail_tui.commands.tree.get_config", return_value=mock_config),
        patch(
            "gmail_tui.commands.tree.get_imap_connection"
        ) as mock_get_imap_connection,
        patch("sys.stdout.write") as mock_stdout_write,
    ):
        # Set up connection mock
        mock_get_imap_connection.return_value.__enter__.return_value = mock_imap_client

        # Call handle method
        args = MagicMock()
        tree_command.handle(args)

        # Verify IMAP connection parameters are correct
        mock_get_imap_connection.assert_called_once_with(
            username=mock_config.email, password=mock_config.app_password
        )

        # Verify folder list was retrieved
        mock_imap_client.list_folders.assert_called_once()

        # Verify output was written (at least once, as each folder prints a line)
        assert mock_stdout_write.call_count >= 1


def test_tree_command_empty_folders(tree_command, mock_config, mock_imap_client):
    """Test handling when no folders are found."""
    # Set up empty folder list
    mock_imap_client.list_folders.return_value = []

    # Mock functions
    with (
        patch("gmail_tui.commands.tree.get_config", return_value=mock_config),
        patch(
            "gmail_tui.commands.tree.get_imap_connection"
        ) as mock_get_imap_connection,
        patch("sys.stdout.write") as mock_stdout_write,
    ):
        # Set up connection mock
        mock_get_imap_connection.return_value.__enter__.return_value = mock_imap_client

        # Call handle method
        args = MagicMock()
        tree_command.handle(args)

        # Verify correct message is displayed
        mock_stdout_write.assert_called_once_with("No folders found\n")


def test_tree_command_connection_error(tree_command, mock_config):
    """Test error handling for connection issues."""
    # Mock functions
    with (
        patch("gmail_tui.commands.tree.get_config", return_value=mock_config),
        patch(
            "gmail_tui.commands.tree.get_imap_connection"
        ) as mock_get_imap_connection,
        patch("sys.stderr.write") as mock_stderr_write,
    ):
        # Set connection to raise exception
        mock_get_imap_connection.side_effect = Exception("Connection error")

        # Call handle method
        args = MagicMock()
        tree_command.handle(args)

        # Verify error message was written
        mock_stderr_write.assert_called_once_with("Error: Connection error\n")


def test_tree_command_nested_folders(tree_command, mock_config, mock_imap_client):
    """Test handling of nested folders."""
    # Set up complex nested folder structure
    mock_imap_client.list_folders.return_value = [
        ([b"\\HasChildren"], b"/", b"Work"),
        ([b"\\HasNoChildren"], b"/", b"Work/Projects"),
        ([b"\\HasNoChildren"], b"/", b"Work/Projects/ProjectA"),
        ([b"\\HasNoChildren"], b"/", b"Work/Projects/ProjectB"),
        ([b"\\HasNoChildren"], b"/", b"Work/Meetings"),
        ([b"\\HasChildren"], b"/", b"Personal"),
        ([b"\\HasNoChildren"], b"/", b"Personal/Family"),
        ([b"\\HasNoChildren"], b"/", b"Personal/Friends"),
    ]

    # Mock functions
    with (
        patch("gmail_tui.commands.tree.get_config", return_value=mock_config),
        patch(
            "gmail_tui.commands.tree.get_imap_connection"
        ) as mock_get_imap_connection,
        patch("sys.stdout.write") as mock_stdout_write,
    ):
        # Set up connection mock
        mock_get_imap_connection.return_value.__enter__.return_value = mock_imap_client

        # Call handle method
        args = MagicMock()
        tree_command.handle(args)

        # Verify output was written (at least once, as each folder prints a line)
        assert mock_stdout_write.call_count >= 1
