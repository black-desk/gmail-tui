"""Tests for the show command.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from unittest.mock import MagicMock, patch

import pytest

from gmail_tui.commands.show import ShowCommand


@pytest.fixture
def show_command():
    """Return a ShowCommand instance for testing."""
    return ShowCommand()


@pytest.mark.parametrize(
    "id_str, folder, format_name, include_headers",
    [
        ("123", "INBOX", "raw", False),
        ("456", "Sent", "json", True),
        ("<msg@example.com>", "[Gmail]/All Mail", "yaml", False),
        ("789", "Drafts", "toml", True),
    ],
)
def test_show_command_handle(id_str, folder, format_name, include_headers):
    """Test if show command handle method correctly processes arguments."""
    show_command = ShowCommand()

    args = MagicMock()
    args.id = id_str
    args.folder = folder
    args.format = format_name
    args.include_headers = include_headers

    with patch("gmail_tui.commands.show.show_email") as mock_show_email:
        show_command.handle(args)
        mock_show_email.assert_called_once_with(id_str, folder, format_name, include_headers)


def test_parse_identifier_uid():
    """Test parsing UID identifier."""
    from gmail_tui.show import parse_identifier

    is_uid, identifier = parse_identifier("123")
    assert is_uid is True
    assert identifier == "123"

    is_uid, identifier = parse_identifier("  456  ")
    assert is_uid is True
    assert identifier == "456"


def test_parse_identifier_message_id():
    """Test parsing Message-ID identifier."""
    from gmail_tui.show import parse_identifier

    is_uid, identifier = parse_identifier("<test@example.com>")
    assert is_uid is False
    assert identifier == "test@example.com"

    is_uid, identifier = parse_identifier("another@example.org")
    assert is_uid is False
    assert identifier == "another@example.org"

    is_uid, identifier = parse_identifier("  <msg@domain.com>  ")
    assert is_uid is False
    assert identifier == "msg@domain.com"


def test_parse_identifier_non_numeric():
    """Test that non-numeric strings are treated as message-ids."""
    from gmail_tui.show import parse_identifier

    is_uid, identifier = parse_identifier("abc")
    assert is_uid is False
    assert identifier == "abc"


def test_output_format_from_str():
    """Test OutputFormat enum parsing."""
    from gmail_tui.show import OutputFormat

    assert OutputFormat.from_str("json") == OutputFormat.JSON
    assert OutputFormat.from_str("JSON") == OutputFormat.JSON
    assert OutputFormat.from_str("yaml") == OutputFormat.YAML
    assert OutputFormat.from_str("toml") == OutputFormat.TOML
    assert OutputFormat.from_str("raw") == OutputFormat.RAW

    with pytest.raises(ValueError):
        OutputFormat.from_str("invalid")


def test_show_email_connection_error(mock_config):
    """Test error handling for connection issues."""
    from gmail_tui.show import show_email

    with (
        patch("gmail_tui.show.get_config", return_value=mock_config),
        patch("gmail_tui.show.get_imap_connection") as mock_get_imap_connection,
        patch("sys.stderr.write") as mock_stderr_write,
    ):
        mock_get_imap_connection.side_effect = Exception("Connection error")
        show_email("123")
        mock_stderr_write.assert_called_once_with("Error: Connection error\n")


def test_show_email_invalid_format(mock_config):
    """Test error handling for invalid output format."""
    from gmail_tui.show import show_email

    with (
        patch("gmail_tui.show.get_config", return_value=mock_config),
        patch("sys.stderr.write") as mock_stderr_write,
    ):
        # This will raise ValueError before trying to connect
        show_email("123", output_format="invalid")
        mock_stderr_write.assert_called()
        error_msg = mock_stderr_write.call_args[0][0]
        assert "Invalid format: invalid" in error_msg
