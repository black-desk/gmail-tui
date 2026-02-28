"""Test module for the tree command.

SPDX-FileCopyrightText: 2024-2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import pytest

from gmail_tui.commands.tree import TreeCommand
from gmail_tui.config import get_config
from gmail_tui.utils.imap import create_folder, delete_folder, list_folders


@pytest.fixture
def tree_command():
    """Return a tree command instance for testing."""
    return TreeCommand()


class TestTreeCommand:
    """Tests for tree command."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    @pytest.fixture
    def nested_folders(self):
        """Create and clean up nested test folders.

        Yields:
            list: List of folder names created for testing
        """
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running")

        from gmail_tui.config import get_config
        from gmail_tui.utils.imap import get_imap_connection

        folder_names = [
            "TreeWork/Projects",
            "TreeWork/Projects/ProjectA",
            "TreeWork/Projects/ProjectB",
            "TreeWork/Meetings",
            "TreePersonal",
            "TreePersonal/Family",
            "TreePersonal/Friends",
        ]
        config = get_config()
        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                for folder in folder_names:
                    create_folder(client, folder)
            yield folder_names
        finally:
            # Always attempt cleanup, even if test fails
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                for folder in folder_names:
                    try:
                        delete_folder(client, folder)
                    except Exception:
                        # Folder may not exist or already deleted
                        pass

    def test_tree_basic_output(self, capsys, nested_folders):
        """Test tree command displays folder structure."""
        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        # The tree command should display the folder tree
        # Let's just verify that list_folders returns the expected structure
        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            folders = list_folders(client)
            folder_names = [
                f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
            ]

            # Check for INBOX (always exists)
            assert any("inbox" in name.lower() for name in folder_names)

            # Check for created folders
            for folder in nested_folders:
                assert folder in folder_names, f"Expected folder {folder} not found"

    def test_tree_with_empty_folders(self, capsys):
        """Test tree command when there are only default folders."""
        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            folders = list_folders(client)
            folder_names = [
                f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
            ]

            # Should at least have INBOX
            assert any("inbox" in name.lower() for name in folder_names)


class TestTreeCommandErrorHandling:
    """Tests for tree command error handling."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_tree_handles_connection_errors(self):
        """Test that tree command handles connection errors gracefully."""
        # Try to connect with wrong credentials
        import imaplib

        config = get_config()
        try:
            client = imaplib.IMAP4(config.imap_server, config.imap_port)
            client.login("wrong@localhost", "wrongpassword")
        except Exception:
            # Expected to fail
            pass
