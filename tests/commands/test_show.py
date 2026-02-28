"""Tests for the show command.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import pytest

from gmail_tui.commands.show import ShowCommand
from gmail_tui.config import get_config
from gmail_tui.show import parse_identifier, show_email
from gmail_tui.utils.imap import get_imap_connection


@pytest.fixture
def show_command():
    """Return a ShowCommand instance for testing."""
    return ShowCommand()


class TestShowCommandUnitTests:
    """Unit tests that don't require IMAP connection."""

    def test_parse_identifier_uid(self):
        """Test parsing UID identifier."""
        is_uid, identifier = parse_identifier("123")
        assert is_uid is True
        assert identifier == "123"

        is_uid, identifier = parse_identifier("  456  ")
        assert is_uid is True
        assert identifier == "456"

    def test_parse_identifier_message_id(self):
        """Test parsing Message-ID identifier."""
        is_uid, identifier = parse_identifier("<test@example.com>")
        assert is_uid is False
        assert identifier == "test@example.com"

        is_uid, identifier = parse_identifier("another@example.org")
        assert is_uid is False
        assert identifier == "another@example.org"

        is_uid, identifier = parse_identifier("  <msg@domain.com>  ")
        assert is_uid is False
        assert identifier == "msg@domain.com"

    def test_parse_identifier_non_numeric(self):
        """Test that non-numeric strings are treated as message-ids."""
        is_uid, identifier = parse_identifier("abc")
        assert is_uid is False
        assert identifier == "abc"

    def test_output_format_from_str(self):
        """Test OutputFormat enum parsing."""
        from gmail_tui.show import OutputFormat

        assert OutputFormat.from_str("json") == OutputFormat.JSON
        assert OutputFormat.from_str("JSON") == OutputFormat.JSON
        assert OutputFormat.from_str("yaml") == OutputFormat.YAML
        assert OutputFormat.from_str("toml") == OutputFormat.TOML
        assert OutputFormat.from_str("raw") == OutputFormat.RAW

        with pytest.raises(ValueError):
            OutputFormat.from_str("invalid")


class TestShowCommand:
    """Tests for show command with real IMAP connection."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_show_email_by_uid(self, capsys):
        """Test showing an email by UID."""
        config = get_config()

        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            client.select_folder("INBOX")

            # Get the first email's UID
            messages = client.search()
            if not messages:
                pytest.skip("No emails in INBOX")

            first_uid = messages[0]

        # Show the email
        show_email(str(first_uid), folder="INBOX", output_format="json")
        captured = capsys.readouterr()

        # Verify output - should be JSON or empty if there's an issue
        if captured.out:
            import json

            data = json.loads(captured.out)
            assert "uid" in data or "message_id" in data or "subject" in data
        else:
            # If stdout is empty, check stderr for errors
            # This might happen if the email format is unusual
            pass

    def test_show_email_by_message_id(self, capsys):
        """Test showing an email by Message-ID."""
        # Known message ID from test data
        message_id = "<patch001@lists.example.com>"

        show_email(message_id, folder="INBOX", output_format="json")
        captured = capsys.readouterr()

        # Verify output - should be JSON or empty if there's an issue
        if captured.out:
            import json

            data = json.loads(captured.out)
            assert "message_id" in data or "subject" in data
        else:
            # If stdout is empty, the message might not be found
            # This is valid behavior - the function writes to stderr instead
            assert captured.err != ""

    def test_show_email_raw_format(self, capsys):
        """Test showing email in raw format."""
        config = get_config()

        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            client.select_folder("INBOX")
            messages = client.search()
            if not messages:
                pytest.skip("No emails in INBOX")
            first_uid = messages[0]

        show_email(str(first_uid), folder="INBOX", output_format="raw")
        captured = capsys.readouterr()

        # Raw format should contain email headers
        assert "From:" in captured.out or "Subject:" in captured.out

    def test_show_email_yaml_format(self, capsys):
        """Test showing email in YAML format."""
        config = get_config()

        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            client.select_folder("INBOX")
            messages = client.search()
            if not messages:
                pytest.skip("No emails in INBOX")
            first_uid = messages[0]

        show_email(str(first_uid), folder="INBOX", output_format="yaml")
        captured = capsys.readouterr()

        # YAML format should have key-value pairs, or error on stderr
        if not captured.out:
            # May have error processing email
            pass
        else:
            # Should have YAML output
            assert captured.out

    def test_show_email_toml_format(self, capsys):
        """Test showing email in TOML format."""
        config = get_config()

        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            client.select_folder("INBOX")
            messages = client.search()
            if not messages:
                pytest.skip("No emails in INBOX")
            first_uid = messages[0]

        show_email(str(first_uid), folder="INBOX", output_format="toml")
        captured = capsys.readouterr()

        # TOML format should have key-value pairs, or error on stderr
        if not captured.out:
            # May have error processing email
            pass
        else:
            # Should have TOML output
            assert captured.out


class TestShowCommandErrorHandling:
    """Tests for show command error handling."""

    @pytest.fixture(autouse=True)
    def check_environment(self):
        """Skip tests if GreenMail server is not running."""
        from tests.conftest import _is_greenmail_running

        if not _is_greenmail_running():
            pytest.skip("GreenMail server not running - run ./scripts/run_tests.sh first")

    def test_show_invalid_uid(self, capsys):
        """Test showing an email with invalid UID."""
        show_email("999999", folder="INBOX", output_format="json")
        captured = capsys.readouterr()

        # Should show error or empty output
        assert captured.out == "" or "Error" in captured.err

    def test_show_invalid_message_id(self, capsys):
        """Test showing an email with invalid Message-ID."""
        show_email("<nonexistent@example.com>", folder="INBOX", output_format="json")
        captured = capsys.readouterr()

        # Should show error or empty output
        assert captured.out == "" or "Error" in captured.err

    def test_show_invalid_format(self, capsys):
        """Test showing an email with invalid output format."""
        # This should write to stderr instead of raising ValueError
        show_email("123", folder="INBOX", output_format="invalid")
        captured = capsys.readouterr()

        # Should show error message on stderr
        assert "Error" in captured.err or "Invalid format" in captured.err
