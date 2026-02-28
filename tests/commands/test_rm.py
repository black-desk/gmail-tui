"""Tests for the rm command.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import pytest

from gmail_tui.commands.rm import RmCommand
from gmail_tui.config import get_config
from gmail_tui.utils.imap import create_folder, delete_folder, list_folders


@pytest.fixture
def rm_command():
    """Return a rm command instance for testing."""
    return RmCommand()


class TestRmCommand:
    """Tests for rm command."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_rm_simple_folder(self):
        """Test deleting a simple folder."""
        folder_name = "TestDeleteFolder"

        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            # Create the folder first
            create_folder(client, folder_name)

            # Verify folder was created
            folders = list_folders(client)
            folder_names = [
                f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
            ]
            assert folder_name in folder_names

            # Delete the folder
            result = delete_folder(client, folder_name)
            assert result is True

            # Verify folder was deleted
            folders = list_folders(client)
            folder_names = [
                f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
            ]
            assert folder_name not in folder_names

    def test_rm_nested_folder(self):
        """Test deleting a nested folder."""
        folder_name = "Work/TestDeleteNested"

        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            # Create the folder
            create_folder(client, folder_name)

            # Verify folder was created
            folders = list_folders(client)
            folder_names = [
                f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
            ]
            assert folder_name in folder_names

            # Delete the folder
            result = delete_folder(client, folder_name)
            assert result is True

            # Verify folder was deleted
            folders = list_folders(client)
            folder_names = [
                f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
            ]
            assert folder_name not in folder_names


class TestRmCommandErrorHandling:
    """Tests for rm command error handling."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_rm_nonexistent_folder(self):
        """Test deleting a non-existent folder."""
        folder_name = "NonExistentDeleteFolder"

        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            # Try to delete non-existent folder
            result = delete_folder(client, folder_name)
            # Should return False for non-existent folder
            assert result is False

    def test_rm_folder_with_children(self):
        """Test deleting a folder that has children."""
        parent = "TestDeleteParent"
        child = "TestDeleteParent/Child"

        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                # Create parent first, then child
                create_folder(client, parent)
                create_folder(client, child)

                # Try to delete parent (should fail because it has children)
                delete_folder(client, parent)

                # Verify parent and child still exist
                folders = list_folders(client)
                folder_names = [
                    f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
                ]
                # Note: The actual behavior depends on the IMAP server
                # For Greenmail, deleting a parent with children silently fails
                # We verify at least the child still exists
                assert child in folder_names
        finally:
            # Cleanup - delete child first, then parent
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                # Delete child, then parent
                try:
                    delete_folder(client, child)
                except Exception:
                    pass
                try:
                    delete_folder(client, parent)
                except Exception:
                    pass
