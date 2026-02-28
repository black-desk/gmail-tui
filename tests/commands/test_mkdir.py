"""Tests for the mkdir command.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import pytest

from gmail_tui.commands.mkdir import MkdirCommand
from gmail_tui.config import get_config
from gmail_tui.utils.imap import create_folder, delete_folder, list_folders


@pytest.fixture
def mkdir_command():
    """Return a mkdir command instance for testing."""
    return MkdirCommand()


class TestMkdirCommand:
    """Tests for mkdir command."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_mkdir_simple_folder(self):
        """Test creating a simple folder."""
        folder_name = "TestSimpleFolder"

        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                # Create the folder
                result = create_folder(client, folder_name)
                assert result is True

                # Verify folder was created
                folders = list_folders(client)
                folder_names = [
                    f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
                ]
                assert folder_name in folder_names
        finally:
            # Cleanup
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                try:
                    delete_folder(client, folder_name)
                except Exception:
                    pass

    def test_mkdir_nested_folder(self):
        """Test creating a nested folder."""
        folder_name = "Work/Projects/TestProject"

        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                # Create the nested folder
                result = create_folder(client, folder_name)
                assert result is True

                # Verify folder was created
                folders = list_folders(client)
                folder_names = [
                    f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
                ]
                assert folder_name in folder_names
        finally:
            # Cleanup
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                try:
                    delete_folder(client, folder_name)
                except Exception:
                    pass

    def test_mkdir_with_special_characters(self):
        """Test creating folders with special characters."""
        folder_name = "Test-Folder_123"

        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                # Create the folder
                result = create_folder(client, folder_name)
                assert result is True

                # Verify folder was created
                folders = list_folders(client)
                folder_names = [
                    f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
                ]
                assert folder_name in folder_names
        finally:
            # Cleanup
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                try:
                    delete_folder(client, folder_name)
                except Exception:
                    pass


class TestMkdirCommandErrorHandling:
    """Tests for mkdir command error handling."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_mkdir_duplicate_folder(self):
        """Test that creating a duplicate folder is handled gracefully."""
        folder_name = "DuplicateFolder"

        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                # Create the folder first time
                create_folder(client, folder_name)

                # Try to create again
                result = create_folder(client, folder_name)
                # Should return False for duplicate (IMAP error)
                # Greenmail logs a warning but doesn't raise exception
                # The function returns False when CREATE fails
                # (the actual result depends on the IMAP server implementation)
                # Greenmail returns False for duplicate
                assert result is False
        finally:
            # Cleanup
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                try:
                    delete_folder(client, folder_name)
                except Exception:
                    pass

    def test_mkdir_invalid_folder_name(self):
        """Test creating a folder with invalid name."""
        # Empty folder name should fail
        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            # Empty folder name
            result = create_folder(client, "")
            # Should return False for invalid folder name
            assert result is False
