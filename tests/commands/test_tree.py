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
