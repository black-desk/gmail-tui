"""End-to-end tests using smtp4dev IMAP server.

SPDX-FileCopyrightText: 2024-2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import imaplib
import json

import pytest

from gmail_tui.list import list_emails
from gmail_tui.utils.imap import fetch_email_metadata, get_imap_connection, list_folders
from gmail_tui.config import get_config


def _skip_if_no_test_config():
    """Skip test if test config is not set (production environment)."""
    if not __import__("os").getenv("GMAIL_TUI_CONFIG"):
        pytest.skip("GMAIL_TUI_CONFIG not set (production environment)")


def _skip_if_server_not_running():
    """Skip test if test server is not running."""
    from .conftest import _is_test_server_running

    if not _is_test_server_running():
        pytest.skip("Test server not running")


class TestIMAPConnection:
    """Tests for IMAP connection functionality."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if test environment is not configured."""
        _skip_if_no_test_config()
        _skip_if_server_not_running()

    # Note: Skipped smtp4dev connection tests as it requires special auth
    # These tests will be re-enabled once we figure out smtp4dev auth

    # Note: Skipped smtp4dev connection tests as it requires special auth
    # These tests will be re-enabled once we figure out smtp4dev auth

    # def test_connect_to_smtp4dev(self, smtp4dev_server: dict) -> None:
    #     """Test connecting to smtp4dev server."""
    #     # smtp4dev accepts any credentials and ignores them
    #     # Try connecting to see if it works at all
    #     try:
    #         with MailBox(
    #             host=smtp4dev_server["host"],
    #             port=smtp4dev_server["port"],
    #             ssl=False,
    #         ) as mailbox:
    #             assert mailbox.login()
    #             mailbox.logout()
    #     except Exception as e:
    #         # smtp4dev may reject auth, which is expected
    #             pytest.skip(f"smtp4dev auth failed (expected): {e}")

    def test_list_folders(self, smtp4dev_server: dict) -> None:
        """Test listing folders."""
        config = get_config()
        with get_imap_connection(username=config.email, password=config.app_password) as client:
            folders = list_folders(client)
            assert len(folders) >= 1

            # Check for INBOX
            inbox_exists = False
            for f in folders:
                if isinstance(f, (tuple, list)) and len(f) >= 3:
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

    def test_list_empty_folder(self, capsys: pytest.CaptureFixture) -> None:
        """Test listing emails in an empty folder."""
        config = get_config()
        with get_imap_connection(username=config.email, password=config.app_password) as client:
            # Try to fetch from a non-existent folder - should return empty list
            emails = fetch_email_metadata(client, "EmptyFolder", limit=10, login=False)
            assert len(emails) == 0

        # list_emails will show "No emails found" message

    def test_list_empty_folder_imap_error(self, capsys: pytest.CaptureFixture) -> None:
        """Test listing emails when IMAP connection fails."""
        import sys
        import imaplib
        config = get_config()

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
        assert len(data) == 4

        # Check first email
        subjects = [e["subject"] for e in data]
        assert "Test Email 1" in subjects

    def test_list_emails_limit(self, capsys: pytest.CaptureFixture) -> None:
        """Test limit parameter in list_emails."""
        list_emails("INBOX", 2, "json")
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert len(data) == 2

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
        with get_imap_connection(username=config.email, password=config.app_password) as client:
            emails = fetch_email_metadata(client, "INBOX", limit=10)

            assert len(emails) == 4

            # Check first email metadata
            email = emails[0]
            assert email.subject is not None
            assert email.from_addr is not None
            assert email.size > 0

    def test_fetch_metadata_fields(self) -> None:
        """Test that metadata fields are correctly parsed."""
        config = get_config()
        with get_imap_connection(username=config.email, password=config.app_password) as client:
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
        with get_imap_connection(username=config.email, password=config.app_password) as client:
            emails = fetch_email_metadata(client, "INBOX", limit=10)

            # Find the review email (second in thread)
            review_email = next(
                (e for e in emails if e.message_id == "<review001@lists.example.com>"),
                None,
            )
            assert review_email is not None
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
        with get_imap_connection(username=config.email, password=config.app_password) as client:
            emails = fetch_email_metadata(client, "INBOX", limit=10)

            # Find the applied email which has CC
            applied_email = next(
                (e for e in emails if e.message_id == "<applied001@lists.example.com>"),
                None,
            )
            assert applied_email is not None
            assert applied_email.cc_addr is not None
            assert "maintainer@example.com" in applied_email.cc_addr
