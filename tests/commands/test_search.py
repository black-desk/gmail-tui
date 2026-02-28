"""Tests for search command.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import json

import pytest

from gmail_tui.commands.search import SearchCommand
from gmail_tui.search import search_emails


@pytest.fixture
def search_command():
    """Return a SearchCommand instance for testing."""
    return SearchCommand()


class TestSearchCommandHandle:
    """Tests for search command handle method."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_search_by_sender(self, capsys):
        """Test searching emails by sender."""
        search_emails(
            folder="INBOX",
            limit=10,
            output_format="json",
            from_addr="sender@example.com",
        )
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert len(data) == 2  # sender@example.com sent 2 emails

        # All results should be from the same sender
        for email in data:
            assert "sender@example.com" in email["from"]

    def test_search_by_subject(self, capsys):
        """Test searching emails by subject."""
        search_emails(
            folder="INBOX",
            limit=10,
            output_format="json",
            subject="Test Email",
        )
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert len(data) == 2  # "Test Email 1" and "Test Email 2"

        # All results should contain "Test Email" in subject
        for email in data:
            assert "Test Email" in email["subject"]

    def test_search_by_subject_patch(self, capsys):
        """Test searching emails by subject with PATCH."""
        search_emails(
            folder="INBOX",
            limit=10,
            output_format="json",
            subject="PATCH",
        )
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        # IMAP SUBJECT search is partial matching, so all emails with PATCH in subject
        # This includes: "[PATCH] Fix memory leak" and two "Re: [PATCH] Fix memory leak"
        assert len(data) == 3

        # All results should contain "PATCH" in subject
        for email in data:
            assert "PATCH" in email["subject"]

    def test_search_by_body(self, capsys):
        """Test searching emails by body content."""
        search_emails(
            folder="INBOX",
            limit=10,
            output_format="json",
            body="patch email",
        )
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert len(data) == 1  # Only patch email contains "patch email"

    def test_search_with_limit(self, capsys):
        """Test search with limit parameter."""
        search_emails(
            folder="INBOX",
            limit=1,
            output_format="json",
            from_addr="sender@example.com",
        )
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert len(data) == 1

    @pytest.mark.parametrize(
        "format_name",
        ["json", "yaml", "toml"],
    )
    def test_search_formats(self, capsys, format_name):
        """Test different output formats."""
        search_emails(
            folder="INBOX",
            limit=1,
            output_format=format_name,
            from_addr="sender@example.com",
        )
        captured = capsys.readouterr()

        if format_name == "json":
            # Basic JSON validation
            data = json.loads(captured.out)
            assert isinstance(data, list)
        else:
            # Basic YAML/TOML validation
            assert captured.out


class TestSearchCommandNoResults:
    """Tests for search that returns no results."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_search_no_results(self, capsys):
        """Test search with no matching results."""
        search_emails(
            folder="INBOX",
            limit=10,
            output_format="json",
            from_addr="nonexistent@example.com",
        )
        captured = capsys.readouterr()

        assert "No emails found" in captured.out

    def test_search_nonexistent_folder(self, capsys):
        """Test searching in a non-existent folder."""
        search_emails(
            folder="NonExistentFolder123",
            limit=10,
            output_format="json",
        )
        captured = capsys.readouterr()

        # Should show error message
        assert "Error" in captured.out or captured.out == ""


class TestSearchCommandErrorHandling:
    """Tests for search command error handling."""

    def test_search_invalid_format(self, capsys):
        """Test search with invalid format."""
        # Invalid format is caught and printed to stderr, not raised
        search_emails(
            folder="INBOX",
            limit=10,
            output_format="invalid",
        )
        captured = capsys.readouterr()

        assert "Error" in captured.err
        assert "Invalid format" in captured.err
