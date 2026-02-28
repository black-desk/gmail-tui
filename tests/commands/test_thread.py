"""Tests for thread command.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import json

import pytest

from gmail_tui.commands.thread import ThreadCommand
from gmail_tui.email import EmailMetadata
from gmail_tui.thread import build_thread_from_emails, find_thread_root, show_thread


@pytest.fixture
def thread_command():
    """Return a ThreadCommand instance for testing."""
    return ThreadCommand()


class TestFindThreadRoot:
    """Tests for find_thread_root function."""

    def test_single_email_is_root(self):
        """Test that a single email with no references is its own root."""
        root = find_thread_root(
            message_id="test@example.com",
            in_reply_to=None,
            references=None,
        )
        assert root == "test@example.com"

    def test_in_reply_to_sets_parent_as_root(self):
        """Test that In-Reply-To header identifies the parent as root."""
        root = find_thread_root(
            message_id="reply@example.com",
            in_reply_to="<parent@example.com>",
            references=None,
        )
        assert root == "parent@example.com"

    def test_references_uses_first_ancestor(self):
        """Test that References header uses the oldest message as root."""
        root = find_thread_root(
            message_id="reply@example.com",
            in_reply_to="<parent@example.com>",
            references="<root@example.com> <parent@example.com>",
        )
        assert root == "root@example.com"

    def test_references_without_in_reply_to(self):
        """Test that References header works without In-Reply-To."""
        root = find_thread_root(
            message_id="reply@example.com",
            in_reply_to=None,
            references="<root@example.com>",
        )
        assert root == "root@example.com"

    def test_multiple_references(self):
        """Test with multiple references."""
        root = find_thread_root(
            message_id="latest@example.com",
            in_reply_to="<recent@example.com>",
            references="<oldest@example.com> <middle@example.com> <recent@example.com>",
        )
        assert root == "oldest@example.com"


class TestBuildThreadFromEmails:
    """Tests for build_thread_from_emails function."""

    def test_single_email_thread(self):
        """Test building a thread from a single email."""
        emails = [
            EmailMetadata(
                uid=1,
                internal_date=None,
                message_id="<test@example.com>",
                from_addr="sender@example.com",
                subject="Test Subject",
            )
        ]

        root, thread_emails = build_thread_from_emails(emails, "test@example.com")

        assert root == "test@example.com"
        assert len(thread_emails) == 1
        assert thread_emails[0].uid == 1

    def test_reply_in_thread(self):
        """Test building a thread with a reply."""
        from datetime import datetime

        now = datetime.now()
        emails = [
            EmailMetadata(
                uid=1,
                internal_date=now,
                message_id="<parent@example.com>",
                from_addr="sender@example.com",
                subject="Original Subject",
            ),
            EmailMetadata(
                uid=2,
                internal_date=now,
                message_id="<reply@example.com>",
                in_reply_to="<parent@example.com>",
                from_addr="replier@example.com",
                subject="Re: Original Subject",
            ),
        ]

        root, thread_emails = build_thread_from_emails(emails, "reply@example.com")

        assert root == "parent@example.com"
        assert len(thread_emails) == 2
        uids = [e.uid for e in thread_emails]
        assert 1 in uids
        assert 2 in uids

    def test_find_thread_by_root_message_id(self):
        """Test finding a thread using the root message ID."""
        emails = [
            EmailMetadata(
                uid=1,
                internal_date=None,
                message_id="<parent@example.com>",
                from_addr="sender@example.com",
                subject="Subject",
            ),
            EmailMetadata(
                uid=2,
                internal_date=None,
                message_id="<reply@example.com>",
                references="<parent@example.com>",
                from_addr="replier@example.com",
                subject="Re: Subject",
            ),
        ]

        root, thread_emails = build_thread_from_emails(emails, "parent@example.com")

        assert root == "parent@example.com"
        assert len(thread_emails) == 2

    def test_multiple_threads(self):
        """Test that only emails from the target thread are returned."""
        emails = [
            EmailMetadata(
                uid=1,
                internal_date=None,
                message_id="<thread1@example.com>",
                from_addr="sender1@example.com",
                subject="Thread 1",
            ),
            EmailMetadata(
                uid=2,
                internal_date=None,
                message_id="<thread1-reply@example.com>",
                references="<thread1@example.com>",
                from_addr="replier1@example.com",
                subject="Re: Thread 1",
            ),
            EmailMetadata(
                uid=3,
                internal_date=None,
                message_id="<thread2@example.com>",
                from_addr="sender2@example.com",
                subject="Thread 2",
            ),
            EmailMetadata(
                uid=4,
                internal_date=None,
                message_id="<thread2-reply@example.com>",
                references="<thread2@example.com>",
                from_addr="replier2@example.com",
                subject="Re: Thread 2",
            ),
        ]

        root, thread_emails = build_thread_from_emails(emails, "thread1-reply@example.com")

        assert root == "thread1@example.com"
        assert len(thread_emails) == 2
        uids = [e.uid for e in thread_emails]
        assert 1 in uids
        assert 2 in uids
        assert 3 not in uids
        assert 4 not in uids

    def test_deep_thread(self):
        """Test building a thread with multiple levels of replies."""
        from datetime import datetime

        now = datetime.now()
        emails = [
            EmailMetadata(
                uid=1,
                internal_date=now,
                message_id="<root@example.com>",
                from_addr="sender@example.com",
                subject="Subject",
            ),
            EmailMetadata(
                uid=2,
                internal_date=now,
                message_id="<reply1@example.com>",
                in_reply_to="<root@example.com>",
                from_addr="replier1@example.com",
                subject="Re: Subject",
            ),
            EmailMetadata(
                uid=3,
                internal_date=now,
                message_id="<reply2@example.com>",
                references="<root@example.com> <reply1@example.com>",
                from_addr="replier2@example.com",
                subject="Re: Subject",
            ),
        ]

        root, thread_emails = build_thread_from_emails(emails, "reply2@example.com")

        assert root == "root@example.com"
        assert len(thread_emails) == 3
        # Emails should be sorted by date (all same in this test)

    def test_thread_emails_sorted_by_date(self):
        """Test that thread emails are sorted by date."""
        from datetime import datetime, timedelta

        now = datetime.now()
        emails = [
            EmailMetadata(
                uid=3,
                internal_date=now + timedelta(hours=2),
                message_id="<reply@example.com>",
                references="<root@example.com>",
                from_addr="replier@example.com",
                subject="Re: Subject",
            ),
            EmailMetadata(
                uid=1,
                internal_date=now,
                message_id="<root@example.com>",
                from_addr="sender@example.com",
                subject="Subject",
            ),
            EmailMetadata(
                uid=2,
                internal_date=now + timedelta(hours=1),
                message_id="<middle@example.com>",
                references="<root@example.com>",
                from_addr="middle@example.com",
                subject="Re: Subject",
            ),
        ]

        root, thread_emails = build_thread_from_emails(emails, "reply@example.com")

        assert len(thread_emails) == 3
        assert thread_emails[0].uid == 1  # Oldest first
        assert thread_emails[1].uid == 2
        assert thread_emails[2].uid == 3

    def test_message_id_not_in_emails(self):
        """Test that ValueError is raised when message ID is not found."""
        emails = [
            EmailMetadata(
                uid=1,
                internal_date=None,
                message_id="<test@example.com>",
                from_addr="sender@example.com",
                subject="Subject",
            )
        ]

        with pytest.raises(ValueError, match="not found in fetched emails"):
            build_thread_from_emails(emails, "nonexistent@example.com")

    def test_standalone_email(self):
        """Test an email that doesn't belong to any thread."""
        emails = [
            EmailMetadata(
                uid=1,
                internal_date=None,
                message_id="<standalone@example.com>",
                from_addr="sender@example.com",
                subject="Standalone",
            )
        ]

        root, thread_emails = build_thread_from_emails(emails, "standalone@example.com")

        assert root == "standalone@example.com"
        assert len(thread_emails) == 1


class TestThreadCommand:
    """Tests for thread command with real IMAP connection."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_show_thread_by_message_id(self, capsys):
        """Test showing a thread by message ID."""
        # Known message ID from test data - using the thread reply
        message_id = "<thread02@lists.example.com>"

        show_thread(message_id, folder="INBOX", output_format="json")
        captured = capsys.readouterr()

        # Verify output structure
        data = json.loads(captured.out)
        assert "thread_root" in data
        assert "email_count" in data
        assert "emails" in data
        assert isinstance(data["emails"], list)
        assert data["email_count"] == len(data["emails"])
        # Should have at least 2 emails (original + reply)
        assert data["email_count"] >= 2

    def test_show_thread_with_custom_folder(self, capsys):
        """Test showing a thread from a specific folder."""
        message_id = "<thread02@lists.example.com>"

        show_thread(message_id, folder="INBOX", output_format="json")
        captured = capsys.readouterr()

        # Should not raise an exception and should have output
        assert captured.out
        data = json.loads(captured.out)
        assert "emails" in data

    @pytest.mark.parametrize(
        "format_name",
        ["json", "yaml", "toml"],
    )
    def test_thread_formats(self, capsys, format_name):
        """Test different output formats."""
        message_id = "<thread02@lists.example.com>"

        show_thread(message_id, folder="INBOX", output_format=format_name)
        captured = capsys.readouterr()

        # Should always have output
        assert captured.out

        if format_name == "json":
            # Validate JSON structure
            data = json.loads(captured.out)
            assert "thread_root" in data
            assert "email_count" in data
            assert "emails" in data

    def test_show_thread_with_angle_brackets(self, capsys):
        """Test showing a thread with angle brackets in message ID."""
        # Test with angle brackets
        message_id = "<thread02@lists.example.com>"

        show_thread(message_id, folder="INBOX", output_format="json")
        captured = capsys.readouterr()

        # Should have output
        assert captured.out
        data = json.loads(captured.out)
        assert "emails" in data

    def test_show_thread_empty_folder(self, capsys):
        """Test showing a thread from an empty folder."""
        from gmail_tui.config import get_config
        from gmail_tui.utils import create_folder, delete_folder, get_imap_connection

        config = get_config()
        temp_folder = "TEMP_EMPTY_THREAD_FOLDER_12345"

        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                create_folder(client, temp_folder)

            # Try to show a thread from the empty folder
            show_thread("any@example.com", folder=temp_folder, output_format="json")
            captured = capsys.readouterr()

            # Should show error message
            assert "No emails found" in captured.err or "Error" in captured.err

        finally:
            # Clean up
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                delete_folder(client, temp_folder)


class TestThreadCommandErrorHandling:
    """Tests for thread command error handling."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_show_thread_invalid_message_id(self, capsys):
        """Test showing a thread with non-existent message ID."""
        show_thread(
            "<nonexistent123456789@example.com>",
            folder="INBOX",
            output_format="json",
        )
        captured = capsys.readouterr()

        # Should show error
        assert "Error" in captured.err or "not found" in captured.err
        assert captured.out == ""

    def test_show_thread_invalid_format(self, capsys):
        """Test showing a thread with invalid output format."""
        show_thread(
            "<thread02@lists.example.com>",
            folder="INBOX",
            output_format="invalid",
        )
        captured = capsys.readouterr()

        # Should show error message on stderr
        assert "Error" in captured.err
        assert "Invalid format" in captured.err


class TestThreadCommandUnitTests:
    """Unit tests that don't require IMAP connection."""

    def test_output_format_from_str(self):
        """Test OutputFormat enum parsing."""
        from gmail_tui.thread import OutputFormat

        assert OutputFormat.from_str("json") == OutputFormat.JSON
        assert OutputFormat.from_str("JSON") == OutputFormat.JSON
        assert OutputFormat.from_str("yaml") == OutputFormat.YAML
        assert OutputFormat.from_str("toml") == OutputFormat.TOML

        with pytest.raises(ValueError):
            OutputFormat.from_str("invalid")
