"""Tests for the list command.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from unittest.mock import MagicMock, patch

import pytest

from gmail_tui.commands.list import ListCommand


@pytest.fixture
def list_command():
    """Return a ListCommand instance for testing."""
    return ListCommand()


@pytest.mark.parametrize(
    "folder, limit, output_format",
    [
        ("INBOX", 10, "json"),
        ("Sent", 5, "yaml"),
        ("[Gmail]/All Mail", 20, "toml"),
    ],
)
def test_list_command_handle(list_command, folder, limit, output_format):
    """Test if the list command correctly processes parameters and outputs results."""
    # Set up parameters
    args = MagicMock()
    args.folder = folder
    args.limit = limit
    args.format = output_format

    # Mock list_emails function
    with patch("gmail_tui.commands.list.list_emails") as mock_list_emails:
        # Call handle method
        list_command.handle(args)

        # Verify list_emails was called correctly
        mock_list_emails.assert_called_once_with(folder, limit, output_format)


def test_list_emails_functionality(mock_config, mock_imap_client):
    """Test the complete functionality of list_emails function."""
    # Import module
    from gmail_tui.list import list_emails

    # Mock IMAP response
    mock_imap_client.search.return_value = [1, 2]
    mock_imap_client.fetch.return_value = {
        1: {
            b"ENVELOPE": (
                b"28-Mar-2024",
                b"Test Email 1",
                ((b"Sender", b"One", b"sender1", b"example.com"),),
                ((b"Sender", b"One", b"sender1", b"example.com"),),
                ((b"Sender", b"One", b"sender1", b"example.com"),),
                ((b"Recipient", b"User", b"user", b"example.com"),),
                None,
                None,
                None,
                b"<message1@example.com>",
            ),
            b"RFC822.SIZE": 1024,
            b"INTERNALDATE": b"28-Mar-2024 12:00:00 +0800",
            b"FLAGS": (b"\\Seen",),
        },
        2: {
            b"ENVELOPE": (
                b"27-Mar-2024",
                b"Test Email 2",
                ((b"Sender", b"Two", b"sender2", b"example.com"),),
                ((b"Sender", b"Two", b"sender2", b"example.com"),),
                ((b"Sender", b"Two", b"sender2", b"example.com"),),
                ((b"Recipient", b"User", b"user", b"example.com"),),
                None,
                None,
                None,
                b"<message2@example.com>",
            ),
            b"RFC822.SIZE": 2048,
            b"INTERNALDATE": b"27-Mar-2024 12:00:00 +0800",
            b"FLAGS": (),
        },
    }

    # Mock functions
    with patch("gmail_tui.list.get_config", return_value=mock_config), patch(
        "gmail_tui.list.connect_imap"
    ) as mock_connect_imap, patch(
        "gmail_tui.list.fetch_email_metadata"
    ) as mock_fetch_email_metadata, patch(
        "builtins.print"
    ) as mock_print:
        # Set up connection mock
        mock_connect_imap.return_value.__enter__.return_value = mock_imap_client

        # Mock fetch_email_metadata to return non-empty list
        mock_fetch_email_metadata.return_value = [MagicMock(), MagicMock()]

        # Call function
        list_emails("INBOX", 10, "json")

        # Verify IMAP connection parameters are correct
        mock_connect_imap.assert_called_once_with(
            username=mock_config.email, password=mock_config.app_password
        )

        # Verify fetch_email_metadata was called
        mock_fetch_email_metadata.assert_called_once_with(mock_imap_client, "INBOX", 10)

        # Verify output was printed
        mock_print.assert_called_once()


def test_list_emails_no_emails(mock_config, mock_imap_client):
    """Test handling when no emails are found."""
    # Import module
    from gmail_tui.list import list_emails

    # Mock functions
    with patch("gmail_tui.list.get_config", return_value=mock_config), patch(
        "gmail_tui.list.connect_imap"
    ) as mock_connect_imap, patch(
        "gmail_tui.list.fetch_email_metadata"
    ) as mock_fetch_email_metadata, patch(
        "builtins.print"
    ) as mock_print:
        # Set up connection mock
        mock_connect_imap.return_value.__enter__.return_value = mock_imap_client

        # Mock fetch_email_metadata to return empty list
        mock_fetch_email_metadata.return_value = []

        # Call function
        list_emails("INBOX", 10, "json")

        # Verify correct message was printed
        mock_print.assert_called_once_with("No emails found in folder: INBOX")


def test_list_emails_connection_error(mock_config):
    """Test error handling for connection issues."""
    # Import module
    from gmail_tui.list import list_emails

    # Mock functions
    with patch("gmail_tui.list.get_config", return_value=mock_config), patch(
        "gmail_tui.list.connect_imap"
    ) as mock_connect_imap, patch("builtins.print") as mock_print:
        # Set connection to raise exception
        mock_connect_imap.side_effect = Exception("Connection error")

        # Call function
        list_emails("INBOX", 10, "json")

        # Verify error message was printed
        mock_print.assert_called_once()
        args, kwargs = mock_print.call_args
        assert "Error: Connection error" in args[0]
        assert kwargs.get("file") is not None  # Should be printed to stderr


@pytest.mark.parametrize("output_format", ["json", "yaml", "toml"])
def test_list_emails_output_formats(mock_config, mock_imap_client, output_format):
    """Test different output formats."""
    # Import module
    from gmail_tui.list import list_emails

    # Mock functions
    with patch("gmail_tui.list.get_config", return_value=mock_config), patch(
        "gmail_tui.list.connect_imap"
    ) as mock_connect_imap, patch(
        "gmail_tui.list.fetch_email_metadata"
    ) as mock_fetch_email_metadata, patch(
        "builtins.print"
    ) as mock_print:
        # Set up connection mock
        mock_connect_imap.return_value.__enter__.return_value = mock_imap_client

        # Mock fetch_email_metadata to return one email
        mock_email = MagicMock()
        mock_email.to_dict.return_value = {"subject": "Test Email"}
        mock_fetch_email_metadata.return_value = [mock_email]

        # Call function
        list_emails("INBOX", 10, output_format)

        # Verify output was printed
        mock_print.assert_called_once()
