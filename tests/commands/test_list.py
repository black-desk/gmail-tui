"""Tests for the list command.

SPDX-FileCopyrightText: 2024-2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import json

import pytest

from gmail_tui.commands.list import ListCommand
from gmail_tui.config import get_config
from gmail_tui.list import list_emails
from gmail_tui.utils.imap import create_folder, delete_folder, fetch_email_metadata


@pytest.fixture
def list_command():
    """Return a ListCommand instance for testing."""
    return ListCommand()


class TestListCommandHandle:
    """Tests for list command handle method."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_list_emails_inbox(self, capsys):
        """Test listing emails in INBOX."""
        list_emails("INBOX", 5, "json")
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert len(data) == 5

        # Check first email
        subjects = [e["subject"] for e in data]
        assert "Test Email 1" in subjects

    def test_list_emails_limit(self, capsys):
        """Test limit parameter in list_emails."""
        list_emails("INBOX", 2, "json")
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert len(data) == 2

    @pytest.mark.parametrize(
        "format_name",
        ["json", "yaml", "toml"],
    )
    def test_list_emails_formats(self, capsys, format_name):
        """Test different output formats."""
        list_emails("INBOX", 1, format_name)
        captured = capsys.readouterr()

        if format_name == "json":
            # Basic JSON validation
            data = json.loads(captured.out)
            assert isinstance(data, list)
        else:
            # Basic YAML/TOML validation
            assert captured.out


class TestListCommandEmptyFolder:
    """Tests for listing emails in an empty folder."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    @pytest.fixture
    def empty_folder(self):
        """Create and clean up an empty folder for testing.

        Yields:
            str: The name of the empty folder
        """
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running")

        folder_name = "EmptyListFolder"
        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                create_folder(client, folder_name)
            yield folder_name
        finally:
            # Always attempt cleanup, even if test fails
            try:
                with get_imap_connection(
                    username=config.email, password=config.app_password
                ) as client:
                    delete_folder(client, folder_name)
            except Exception:
                # Folder may not exist or already deleted
                pass

    def test_list_empty_folder(self, capsys, empty_folder):
        """Test listing emails in an empty folder."""
        config = get_config()
        from gmail_tui.utils.imap import get_imap_connection

        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            emails = fetch_email_metadata(client, empty_folder, limit=10)
            assert len(emails) == 0


class TestListCommandInvalidFolder:
    """Tests for handling invalid folder names."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_list_nonexistent_folder(self, capsys):
        """Test listing emails from a non-existent folder."""
        list_emails("NonExistentFolder123", 10, "json")
        captured = capsys.readouterr()

        # Should show error message
        assert "Error" in captured.out or captured.out == ""
