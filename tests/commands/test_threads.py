"""Tests for threads command.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import json

import pytest

from gmail_tui.commands.threads import ThreadsCommand
from gmail_tui.threads import EmailThread, build_threads, list_threads
from gmail_tui.email import EmailMetadata


@pytest.fixture
def threads_command():
    """Return a ThreadsCommand instance for testing."""
    return ThreadsCommand()


class TestThreadsCommandHandle:
    """Tests for threads command handle method."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_list_threads_default(self, capsys):
        """Test listing threads with default parameters."""
        list_threads(folder="INBOX", limit=20, output_format="json")
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert isinstance(data, list)

    def test_list_threads_with_limit(self, capsys):
        """Test listing threads with limit."""
        list_threads(folder="INBOX", limit=1, output_format="json")
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert isinstance(data, list)
        # Should have at most 1 thread
        assert len(data) <= 1

    @pytest.mark.parametrize(
        "format_name",
        ["json", "yaml", "toml"],
    )
    def test_threads_formats(self, capsys, format_name):
        """Test different output formats."""
        list_threads(folder="INBOX", limit=5, output_format=format_name)
        captured = capsys.readouterr()

        if format_name == "json":
            # Basic JSON validation
            data = json.loads(captured.out)
            assert isinstance(data, list)
        else:
            # Basic YAML/TOML validation
            assert captured.out


class TestBuildThreads:
    """Tests for thread building logic."""

    def test_single_email_creates_single_thread(self):
        """Test that a single email creates a single thread."""
        emails = [
            EmailMetadata(
                uid=1,
                internal_date=None,
                message_id="<test1@example.com>",
                from_addr="sender@example.com",
                subject="Test Subject",
            )
        ]

        threads = build_threads(emails)

        assert len(threads) == 1
        assert threads[0].thread_id == "test1@example.com"
        assert threads[0].email_count == 1
        assert threads[0].subject == "Test Subject"
        assert "sender@example.com" in threads[0].participants

    def test_reply_creates_thread_with_parent(self):
        """Test that replies are grouped into the same thread."""
        emails = [
            EmailMetadata(
                uid=1,
                internal_date=None,
                message_id="<parent@example.com>",
                from_addr="sender@example.com",
                subject="Test Subject",
            ),
            EmailMetadata(
                uid=2,
                internal_date=None,
                message_id="<reply@example.com>",
                in_reply_to="<parent@example.com>",
                from_addr="replier@example.com",
                subject="Re: Test Subject",
            ),
        ]

        threads = build_threads(emails)

        assert len(threads) == 1
        assert threads[0].thread_id == "parent@example.com"
        assert threads[0].email_count == 2
        assert "sender@example.com" in threads[0].participants
        assert "replier@example.com" in threads[0].participants

    def test_multiple_threads(self):
        """Test that separate conversations create separate threads."""
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
                message_id="<thread2@example.com>",
                from_addr="sender2@example.com",
                subject="Thread 2",
            ),
        ]

        threads = build_threads(emails)

        assert len(threads) == 2
        thread_ids = {t.thread_id for t in threads}
        assert "thread1@example.com" in thread_ids
        assert "thread2@example.com" in thread_ids

    def test_references_header_creates_thread(self):
        """Test that References header is used for thread grouping."""
        emails = [
            EmailMetadata(
                uid=1,
                internal_date=None,
                message_id="<root@example.com>",
                from_addr="sender@example.com",
                subject="Thread Subject",
            ),
            EmailMetadata(
                uid=2,
                internal_date=None,
                message_id="<reply1@example.com>",
                references="<root@example.com>",
                from_addr="replier1@example.com",
                subject="Re: Thread Subject",
            ),
            EmailMetadata(
                uid=3,
                internal_date=None,
                message_id="<reply2@example.com>",
                references="<root@example.com> <reply1@example.com>",
                from_addr="replier2@example.com",
                subject="Re: Thread Subject",
            ),
        ]

        threads = build_threads(emails)

        assert len(threads) == 1
        assert threads[0].thread_id == "root@example.com"
        assert threads[0].email_count == 3

    def test_threads_sorted_by_date(self):
        """Test that threads are sorted by latest email date."""
        from datetime import datetime, timedelta

        now = datetime.now()
        emails = [
            EmailMetadata(
                uid=1,
                internal_date=now,
                message_id="<thread1@example.com>",
                from_addr="sender1@example.com",
                subject="Thread 1",
            ),
            EmailMetadata(
                uid=2,
                internal_date=now - timedelta(days=1),
                message_id="<thread2@example.com>",
                from_addr="sender2@example.com",
                subject="Thread 2",
            ),
        ]

        threads = build_threads(emails)

        assert len(threads) == 2
        # First thread should be the one with the latest date
        assert threads[0].thread_id == "thread1@example.com"
        assert threads[1].thread_id == "thread2@example.com"


class TestEmailThread:
    """Tests for EmailThread class."""

    def test_add_email_increments_count(self):
        """Test that adding emails increments the count."""
        thread = EmailThread(thread_id="test@example.com")

        assert thread.email_count == 0

        email1 = EmailMetadata(
            uid=1,
            internal_date=None,
            message_id="<msg1@example.com>",
            from_addr="sender1@example.com",
            subject="Subject",
        )
        thread.add_email(email1)

        assert thread.email_count == 1

        email2 = EmailMetadata(
            uid=2,
            internal_date=None,
            message_id="<msg2@example.com>",
            from_addr="sender2@example.com",
            subject="Subject",
        )
        thread.add_email(email2)

        assert thread.email_count == 2

    def test_add_email_updates_participants(self):
        """Test that adding emails updates participants."""
        thread = EmailThread(thread_id="test@example.com")

        email1 = EmailMetadata(
            uid=1,
            internal_date=None,
            message_id="<msg1@example.com>",
            from_addr="sender1@example.com",
            subject="Subject",
        )
        thread.add_email(email1)

        assert "sender1@example.com" in thread.participants

        email2 = EmailMetadata(
            uid=2,
            internal_date=None,
            message_id="<msg2@example.com>",
            from_addr="sender2@example.com",
            subject="Subject",
        )
        thread.add_email(email2)

        assert "sender1@example.com" in thread.participants
        assert "sender2@example.com" in thread.participants

    def test_to_dict(self):
        """Test to_dict method."""
        thread = EmailThread(thread_id="test@example.com", subject="Test Subject")

        email = EmailMetadata(
            uid=1,
            internal_date=None,
            message_id="<msg1@example.com>",
            from_addr="sender1@example.com",
            subject="Test Subject",
        )
        thread.add_email(email)

        result = thread.to_dict()

        assert result["thread_id"] == "test@example.com"
        assert result["email_count"] == 1
        assert result["subject"] == "Test Subject"
        assert "sender1@example.com" in result["participants"]
        assert [1] == result["email_uids"]


class TestThreadsCommandNoResults:
    """Tests for threads command that returns no results."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_threads_no_results_empty_folder(self, capsys):
        """Test listing threads from an empty folder."""
        # Create a temporary empty folder
        from gmail_tui.config import get_config
        from gmail_tui.utils import create_folder, delete_folder, get_imap_connection

        config = get_config()
        temp_folder = "TEMP_EMPTY_FOLDER_12345"

        try:
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                create_folder(client, temp_folder)

            # Try to list threads from the empty folder
            list_threads(folder=temp_folder, limit=10, output_format="json")
            captured = capsys.readouterr()

            assert "No emails found" in captured.out

        finally:
            # Clean up
            with get_imap_connection(
                username=config.email, password=config.app_password
            ) as client:
                delete_folder(client, temp_folder)


class TestThreadsCommandErrorHandling:
    """Tests for threads command error handling."""

    def test_threads_invalid_format(self, capsys):
        """Test threads with invalid format."""
        # Invalid format is caught and printed to stderr, not raised
        list_threads(folder="INBOX", limit=10, output_format="invalid")
        captured = capsys.readouterr()

        assert "Error" in captured.err
        assert "Invalid format" in captured.err
