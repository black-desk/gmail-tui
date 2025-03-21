"""Tests for the tree command.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from unittest.mock import MagicMock, patch

import pytest

from gmail_tui.commands.tree import TreeCommand


@pytest.fixture
def tree_command():
    """Return a TreeCommand instance for testing."""
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
        patch("gmail_tui.commands.tree.connect_imap") as mock_connect_imap,
        patch("builtins.print") as mock_print,
    ):
        # Set up connection mock
        mock_connect_imap.return_value.__enter__.return_value = mock_imap_client

        # Call handle method
        args = MagicMock()
        tree_command.handle(args)

        # Verify IMAP connection parameters are correct
        mock_connect_imap.assert_called_once_with(
            username=mock_config.email, password=mock_config.app_password
        )

        # Verify folder list was retrieved
        mock_imap_client.list_folders.assert_called_once()

        # Verify output was printed (at least once, as each folder prints a line)
        assert mock_print.call_count >= 1

        # Verify output contains mailbox folder names
        all_output = "".join(
            [call[0][0] for call in mock_print.call_args_list if len(call[0]) > 0]
        )
        assert "INBOX" in all_output
        assert "[Gmail]" in all_output
        assert "All Mail" in all_output


def test_tree_command_empty_folders(tree_command, mock_config, mock_imap_client):
    """Test handling when no folders are found."""
    # Set up empty folder list
    mock_imap_client.list_folders.return_value = []

    # Mock functions
    with (
        patch("gmail_tui.commands.tree.get_config", return_value=mock_config),
        patch("gmail_tui.commands.tree.connect_imap") as mock_connect_imap,
        patch("builtins.print") as mock_print,
    ):
        # Set up connection mock
        mock_connect_imap.return_value.__enter__.return_value = mock_imap_client

        # Call handle method
        args = MagicMock()
        tree_command.handle(args)

        # Verify correct message was printed
        mock_print.assert_called_once_with("No folders found")


def test_tree_command_connection_error(tree_command, mock_config):
    """Test error handling for connection issues."""
    # Mock functions
    with (
        patch("gmail_tui.commands.tree.get_config", return_value=mock_config),
        patch("gmail_tui.commands.tree.connect_imap") as mock_connect_imap,
        patch("builtins.print") as mock_print,
    ):
        # Set connection to raise exception
        mock_connect_imap.side_effect = Exception("Connection error")

        # Call handle method
        args = MagicMock()
        tree_command.handle(args)

        # Verify error message was printed
        mock_print.assert_called_once()
        args, kwargs = mock_print.call_args
        assert "Error: Connection error" in args[0]
        assert kwargs.get("file") is not None  # Should be printed to stderr


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
        patch("gmail_tui.commands.tree.connect_imap") as mock_connect_imap,
        patch("builtins.print") as mock_print,
    ):
        # Set up connection mock
        mock_connect_imap.return_value.__enter__.return_value = mock_imap_client

        # Call handle method
        args = MagicMock()
        tree_command.handle(args)

        # Verify printed output contains all folder names
        all_output = "".join(
            [call[0][0] for call in mock_print.call_args_list if len(call[0]) > 0]
        )
        assert "Work" in all_output
        assert "Projects" in all_output
        assert "ProjectA" in all_output
        assert "Personal" in all_output
        assert "Family" in all_output

        # Verify nested structure (check indentation)
        calls = [call[0][0] for call in mock_print.call_args_list if len(call[0]) > 0]

        # Find top-level and subdirectory lines
        work_line = next(
            (line for line in calls if "Work" in line and "Projects" not in line), None
        )
        projects_line = next(
            (line for line in calls if "Projects" in line and "ProjectA" not in line),
            None,
        )
        project_a_line = next((line for line in calls if "ProjectA" in line), None)

        # Check indentation levels (subdirectories should be more indented)
        if work_line and projects_line and project_a_line:
            work_indent = len(work_line) - len(work_line.lstrip())
            projects_indent = len(projects_line) - len(projects_line.lstrip())
            project_a_indent = len(project_a_line) - len(project_a_line.lstrip())

            assert projects_indent > work_indent
            assert project_a_indent > projects_indent
