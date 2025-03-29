"""Tests for the list command.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later

These tests focus on the public interfaces and mock the IMAP server responses directly,
rather than mocking internal implementation details like EmailMetadata objects.
This approach ensures that tests remain valid even when internal implementations change,
as long as the public interfaces and expected behaviors remain the same.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from imapclient.response_types import Envelope

from gmail_tui.commands.list import ListCommand


# Helper function to create IMAP envelope response
def create_envelope(subject, from_addr, to_addr, date=None, message_id=None):
    """Create a mock IMAP envelope response."""
    if date is None:
        date = b"01-Jan-2023"
    if message_id is None:
        message_id = b"<test@example.com>"

    return Envelope(
        date,
        subject,
        (from_addr,),  # from_addr
        (from_addr,),  # sender
        (from_addr,),  # reply_to
        (to_addr,),  # to
        None,  # cc
        None,  # bcc
        None,  # in_reply_to
        message_id,
    )


@pytest.fixture
def list_command():
    """Return a ListCommand instance for testing."""
    return ListCommand()


@pytest.mark.parametrize(
    "folder, limit, format_name",
    [
        ("INBOX", 10, "json"),
        ("Sent", 5, "yaml"),
        ("[Gmail]/All Mail", 20, "toml"),
    ],
)
def test_list_command_handle(folder, limit, format_name):
    """Test if list command handle method correctly processes arguments."""
    # Create command
    list_command = ListCommand()

    # Create args mock
    args = MagicMock()
    args.folder = folder
    args.limit = limit
    args.format = format_name

    # Mock the list_emails function
    with patch("gmail_tui.commands.list.list_emails") as mock_list_emails:
        # Call handle method
        list_command.handle(args)

        # Verify list_emails was called with correct arguments (positional)
        mock_list_emails.assert_called_once_with(folder, limit, format_name)


def test_list_emails_functionality(mock_config, mock_imap_client):
    """Test the complete functionality of list_emails function."""
    # Import module
    from gmail_tui.list import list_emails

    # Mock IMAP server responses directly rather than mocking internal EmailMetadata
    # objects
    mock_imap_client.search.return_value = [1, 2]

    # Setup IMAP response with proper Envelope objects
    from_addr = (b"Sender Name", b"", b"sender", b"example.com")
    to_addr = (b"Recipient", b"", b"user", b"example.com")

    mock_imap_client.fetch.return_value = {
        1: {
            b"ENVELOPE": create_envelope(
                b"Test Email 1",
                from_addr,
                to_addr,
                message_id=b"<message1@example.com>"
            ),
            b"RFC822.SIZE": 1024,
            b"INTERNALDATE": datetime.now(),
            b"FLAGS": (b"\\Seen",),
        },
        2: {
            b"ENVELOPE": create_envelope(
                b"Test Email 2",
                from_addr,
                to_addr,
                message_id=b"<message2@example.com>"
            ),
            b"RFC822.SIZE": 2048,
            b"INTERNALDATE": datetime.now(),
            b"FLAGS": (),
        },
    }

    # Mock functions
    with (
        patch("gmail_tui.list.get_config", return_value=mock_config),
        patch("gmail_tui.list.connect_imap") as mock_connect_imap,
        patch("sys.stdout.write") as mock_stdout_write,
    ):
        # Set up connection mock
        mock_connect_imap.return_value.__enter__.return_value = mock_imap_client

        # Call function
        list_emails("INBOX", 10, "json")

        # Verify IMAP connection parameters are correct
        mock_connect_imap.assert_called_once_with(
            username=mock_config.email, password=mock_config.app_password
        )

        # Verify IMAP methods were called with correct parameters
        mock_imap_client.select_folder.assert_called_once_with("INBOX")
        mock_imap_client.search.assert_called_once()
        mock_imap_client.fetch.assert_called_once()

        # Verify output was written to stdout
        assert mock_stdout_write.call_count >= 1


def test_list_emails_no_emails(mock_config, mock_imap_client):
    """Test handling when no emails are found."""
    # Import module
    from gmail_tui.list import list_emails

    # Mock empty search results
    mock_imap_client.search.return_value = []

    # Mock functions
    with (
        patch("gmail_tui.list.get_config", return_value=mock_config),
        patch("gmail_tui.list.connect_imap") as mock_connect_imap,
        patch("sys.stdout.write") as mock_stdout_write,
    ):
        # Set up connection mock
        mock_connect_imap.return_value.__enter__.return_value = mock_imap_client

        # Call function
        list_emails("INBOX", 10, "json")

        # Verify correct message was written to stdout
        mock_stdout_write.assert_called_once_with("No emails found in folder: INBOX\n")


def test_list_emails_connection_error(mock_config):
    """Test error handling for connection issues."""
    # Import module
    from gmail_tui.list import list_emails

    # Mock functions
    with (
        patch("gmail_tui.list.get_config", return_value=mock_config),
        patch("gmail_tui.list.connect_imap") as mock_connect_imap,
        patch("sys.stderr.write") as mock_stderr_write,
    ):
        # Set connection to raise exception
        mock_connect_imap.side_effect = Exception("Connection error")

        # Call function
        list_emails("INBOX", 10, "json")

        # Verify error message was written to stderr
        mock_stderr_write.assert_called_once_with("Error: Connection error\n")


@pytest.mark.parametrize("output_format", ["json", "yaml", "toml"])
def test_list_emails_output_formats(mock_config, mock_imap_client, output_format):
    """Test different output formats."""
    # Import module
    from gmail_tui.list import list_emails

    # Mock IMAP server response with a single email
    mock_imap_client.search.return_value = [1]

    # Setup IMAP response with proper Envelope objects
    from_addr = (b"Sender Name", b"", b"sender", b"example.com")
    to_addr = (b"Recipient", b"", b"user", b"example.com")

    mock_imap_client.fetch.return_value = {
        1: {
            b"ENVELOPE": create_envelope(
                b"Test Email Format",
                from_addr,
                to_addr
            ),
            b"RFC822.SIZE": 1024,
            b"INTERNALDATE": datetime.now(),
            b"FLAGS": (b"\\Seen",),
        }
    }

    # Mock functions
    with (
        patch("gmail_tui.list.get_config", return_value=mock_config),
        patch("gmail_tui.list.connect_imap") as mock_connect_imap,
        patch("sys.stdout.write") as mock_stdout_write,
    ):
        # Set up connection mock
        mock_connect_imap.return_value.__enter__.return_value = mock_imap_client

        # Call function
        list_emails("INBOX", 10, output_format)

        # Verify output was written to stdout
        assert mock_stdout_write.call_count >= 1
