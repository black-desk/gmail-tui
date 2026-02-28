"""Tests for the mv command.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import pytest

from gmail_tui.commands.mv import MvCommand
from gmail_tui.config import get_config
from gmail_tui.utils.imap import create_folder, delete_folder, list_folders, rename_folder


@pytest.fixture
def mv_command():
    """Return a mv command instance for testing."""
    return MvCommand()


class TestMvCommand:
    """Tests for mv command."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_mv_simple_rename(self):
        """Test renaming a simple folder."""
        old_name = "OldTestFolder"
        new_name = "NewTestFolder"

        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                # Create the original folder
                create_folder(client, old_name)

                # Rename the folder
                result = rename_folder(client, old_name, new_name)
                assert result is True

                # Verify rename happened
                folders = list_folders(client)
                folder_names = [
                    f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
                ]
                assert old_name not in folder_names
                assert new_name in folder_names
        finally:
            # Cleanup
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                for folder in [old_name, new_name]:
                    try:
                        delete_folder(client, folder)
                    except Exception:
                        pass

    def test_mv_nested_folder(self):
        """Test renaming a nested folder."""
        old_name = "Work/OldProject"
        new_name = "Work/NewProject"

        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                # Create the original folder (parent created automatically by Greenmail)
                create_folder(client, old_name)

                # Rename the folder
                result = rename_folder(client, old_name, new_name)
                assert result is True

                # Verify rename happened
                folders = list_folders(client)
                folder_names = [
                    f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
                ]
                assert old_name not in folder_names
                assert new_name in folder_names
        finally:
            # Cleanup
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                for folder in [old_name, new_name]:
                    try:
                        delete_folder(client, folder)
                    except Exception:
                        pass

    def test_mv_move_to_different_hierarchy(self):
        """Test moving a folder to a different hierarchy."""
        old_name = "TestMoveFolder"
        new_name = "Archived/TestMoveFolder"

        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                # Create the original folder
                create_folder(client, old_name)

                # Move/rename the folder
                result = rename_folder(client, old_name, new_name)
                assert result is True

                # Verify move happened
                folders = list_folders(client)
                folder_names = [
                    f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
                ]
                assert old_name not in folder_names
                assert new_name in folder_names
        finally:
            # Cleanup
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                for folder in [old_name, new_name]:
                    try:
                        delete_folder(client, folder)
                    except Exception:
                        pass


class TestMvCommandErrorHandling:
    """Tests for mv command error handling."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_mv_nonexistent_folder(self):
        """Test moving a non-existent folder."""
        old_name = "NonExistentFolder"
        new_name = "NewName"

        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            # Try to rename non-existent folder
            result = rename_folder(client, old_name, new_name)
            # Should return False for non-existent folder
            assert result is False

    def test_mv_to_existing_name(self):
        """Test moving to a folder name that already exists."""
        old_name = "Folder1"
        new_name = "Folder2"

        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                # Create both folders
                create_folder(client, old_name)
                create_folder(client, new_name)

                # Try to rename to existing name
                result = rename_folder(client, old_name, new_name)
                # Should return False for duplicate name
                assert result is False
        finally:
            # Cleanup
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                for folder in [old_name, new_name]:
                    try:
                        delete_folder(client, folder)
                    except Exception:
                        pass
