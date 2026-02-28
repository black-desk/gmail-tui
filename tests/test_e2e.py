"""End-to-end tests using smtp4dev IMAP server.

SPDX-FileCopyrightText: 2024-2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import imaplib
import json

import pytest

from gmail_tui.config import get_config
from gmail_tui.list import list_emails
from gmail_tui.utils.imap import (
    create_folder,
    delete_folder,
    fetch_email_metadata,
    get_imap_connection,
    list_folders,
)

# Test constants
FOLDER_MIN_FIELDS = 3
EXPECTED_EMAIL_COUNT = 5
LIMIT_EMAIL_COUNT = 2


def _skip_if_no_test_config():
    """Skip test if test config is not set (production environment)."""
    if not __import__("os").getenv("GMAIL_TUI_CONFIG"):
        pytest.skip("GMAIL_TUI_CONFIG not set (production environment)")


def _skip_if_server_not_running():
    """Skip test if test server is not running."""
    from .conftest import _is_greenmail_running

    if not _is_greenmail_running():
        pytest.skip("GreenMail server not running")


class TestIMAPConnection:
    """Tests for IMAP connection functionality."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if test environment is not configured."""
        _skip_if_no_test_config()
        _skip_if_server_not_running()

    def test_list_folders(self, greenmail_server) -> None:  # noqa: ARG002
        """Test listing folders."""
        config = get_config()
        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            folders = list_folders(client)
            assert len(folders) >= 1

            # Check for INBOX
            inbox_exists = False
            for f in folders:
                if isinstance(f, tuple | list) and len(f) >= FOLDER_MIN_FIELDS:
                    folder_name = f[2]
                    if isinstance(folder_name, bytes):
                        folder_name = folder_name.decode()
                    elif isinstance(folder_name, int):
                        # Skip numeric folder names (flags or counts)
                        continue
                    if folder_name.lower() == "inbox":
                        inbox_exists = True
                        break
            assert inbox_exists


class TestListEmails:
    """Tests for listing emails."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if test environment is not configured."""
        _skip_if_no_test_config()
        _skip_if_server_not_running()

    @pytest.fixture
    def empty_folder(self):
        """Create and clean up an empty folder for testing.

        Yields:
            str: The name of the empty folder
        """
        folder_name = "EmptyFolder"
        config = get_config()
        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                create_folder(client, folder_name)
            yield folder_name
        finally:
            # Always attempt cleanup, even if test fails
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                try:
                    delete_folder(client, folder_name)
                except Exception:
                    # Folder may not exist or already deleted
                    pass

    def test_list_empty_folder(
        self, capsys: pytest.CaptureFixture, empty_folder: str  # noqa: ARG002
    ) -> None:
        """Test listing emails in an empty folder."""
        config = get_config()
        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            # Fetch from the empty folder
            emails = fetch_email_metadata(client, empty_folder, limit=10)
            assert len(emails) == 0

        # list_emails will show "No emails found" message

    def test_list_empty_folder_imap_error(self, capsys: pytest.CaptureFixture) -> None:  # noqa: ARG002
        """Test listing emails when IMAP connection fails."""
        import sys

        # Try to connect with wrong credentials
        try:
            client = imaplib.IMAP4("localhost", 143)
            client.login("test", "wrong")
        except Exception as e:
            sys.stdout.write(f"Expected error: {e}\n")

    def test_list_emails_with_content(self, capsys: pytest.CaptureFixture) -> None:
        """Test listing emails when folder has content."""
        list_emails("INBOX", 10, "json")
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert len(data) == EXPECTED_EMAIL_COUNT

        # Check first email
        subjects = [e["subject"] for e in data]
        assert "Test Email 1" in subjects

    def test_list_emails_limit(self, capsys: pytest.CaptureFixture) -> None:
        """Test limit parameter in list_emails."""
        list_emails("INBOX", LIMIT_EMAIL_COUNT, "json")
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert len(data) == LIMIT_EMAIL_COUNT

    def test_list_emails_yaml_format(self, capsys: pytest.CaptureFixture) -> None:
        """Test YAML output format."""
        list_emails("INBOX", 1, "yaml")
        captured = capsys.readouterr()

        # Basic YAML validation
        assert "- " in captured.out  # YAML list indicator
        assert "subject:" in captured.out


class TestFetchEmailMetadata:
    """Tests for fetching email metadata."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if test environment is not configured."""
        _skip_if_no_test_config()
        _skip_if_server_not_running()

    def test_fetch_metadata(self) -> None:
        """Test fetching email metadata."""
        config = get_config()
        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            emails = fetch_email_metadata(client, "INBOX", limit=10)

            assert len(emails) == EXPECTED_EMAIL_COUNT

            # Check first email metadata
            email = emails[0]
            assert email.subject is not None
            assert email.from_addr is not None
            assert email.size > 0

    def test_fetch_metadata_fields(self) -> None:
        """Test that metadata fields are correctly parsed."""
        config = get_config()
        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            emails = fetch_email_metadata(client, "INBOX", limit=10)

            # Find the patch email
            patch_email = next(
                (e for e in emails if e.subject == "[PATCH] Fix memory leak"), None
            )
            assert patch_email is not None
            assert "bob@example.com" in patch_email.from_addr
            assert patch_email.message_id == "<patch001@lists.example.com>"


class TestEmailThread:
    """Tests for email threading via References header."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if test environment is not configured."""
        _skip_if_no_test_config()
        _skip_if_server_not_running()

    def test_thread_references(self) -> None:
        """Test that thread emails have proper references."""
        config = get_config()
        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            emails = fetch_email_metadata(client, "INBOX", limit=10)

            # Find the review email (second in thread)
            review_email = next(
                (e for e in emails if e.message_id == "<review001@lists.example.com>"),
                None,
            )
            assert review_email is not None
            # Note: in_reply_to from ENVELOPE structure
            assert review_email.in_reply_to == "<patch001@lists.example.com>"

            # Find the applied email (third in thread)
            applied_email = next(
                (e for e in emails if e.message_id == "<applied001@lists.example.com>"),
                None,
            )
            assert applied_email is not None
            assert applied_email.in_reply_to == "<review001@lists.example.com>"

    def test_cc_recipients(self) -> None:
        """Test that CC recipients are correctly parsed."""
        config = get_config()
        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            emails = fetch_email_metadata(client, "INBOX", limit=10)

            # Find the applied email which has CC
            applied_email = next(
                (e for e in emails if e.message_id == "<applied001@lists.example.com>"),
                None,
            )
            assert applied_email is not None
            assert applied_email.cc_addr is not None
            assert "maintainer@example.com" in applied_email.cc_addr


class TestFolderOperations:
    """Tests for folder management operations."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if test environment is not configured."""
        _skip_if_no_test_config()
        _skip_if_server_not_running()

    def test_create_and_delete_folder(self) -> None:
        """Test creating and deleting a folder."""
        config = get_config()
        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            # Create a test folder
            assert create_folder(client, "TestFolder")
            folders = list_folders(client)
            folder_names = [
                f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
            ]
            assert "TestFolder" in folder_names

            # Delete the test folder
            assert delete_folder(client, "TestFolder")
            folders = list_folders(client)
            folder_names = [
                f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
            ]
            assert "TestFolder" not in folder_names

    @pytest.fixture
    def test_folders(self):
        """Create and clean up nested test folders.

        Yields:
            list: List of folder names created for testing
        """
        folder_names = ["Work/Projects", "Work/Meetings", "Personal"]
        config = get_config()
        try:
            # Create nested folders
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                create_folder(client, "Work/Projects")
                create_folder(client, "Work/Projects/ProjectA")
                create_folder(client, "Work/Projects/ProjectB")
                create_folder(client, "Work/Meetings")
                create_folder(client, "Personal")
                create_folder(client, "Personal/Family")
                create_folder(client, "Personal/Friends")
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

    def test_create_nested_folders(self, test_folders: list) -> None:  # noqa: ARG002
        """Test creating nested folders."""
        config = get_config()
        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            folders = list_folders(client)
            folder_names = [
                f[2].decode() if isinstance(f[2], bytes) else str(f[2]) for f in folders
            ]

            # Verify all folders were created
            assert "Work/Projects" in folder_names
            assert "Work/Projects/ProjectA" in folder_names
            assert "Work/Projects/ProjectB" in folder_names
            assert "Work/Meetings" in folder_names
            assert "Personal" in folder_names
            assert "Personal/Family" in folder_names
            assert "Personal/Friends" in folder_names
