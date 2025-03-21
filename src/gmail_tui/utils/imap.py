"""IMAP utilities for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black_desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from typing import Optional

from imapclient import IMAPClient

from gmail_tui.email import EmailMetadata


def connect_imap(username: str, password: str) -> IMAPClient:
    """Connect to Gmail IMAP server.

    Args:
        username: Gmail address
        password: App password for Gmail

    Returns:
        IMAPClient object

    """
    client = IMAPClient("imap.gmail.com")
    client.login(username, password)
    return client


def fetch_email_metadata(
    client: IMAPClient,
    folder: str,
    limit: int = 20,
    search_criteria: Optional[list[str]] = None,
) -> list[EmailMetadata]:
    """Fetch email metadata from IMAP server.

    Args:
        client: IMAPClient object
        folder: Folder name to fetch emails from
        limit: Maximum number of emails to fetch
        search_criteria: List of IMAP search criteria

    Returns:
        List of EmailMetadata objects

    """
    if search_criteria is None:
        search_criteria = ["ALL"]
    client.select_folder(folder)

    # Search for messages
    messages = client.search(search_criteria)

    # Optimization: only fetch email metadata, not the full content
    # Use ENVELOPE for basic info, RFC822.SIZE for size, INTERNALDATE for date
    fetch_data = client.fetch(
        messages, ["ENVELOPE", "INTERNALDATE", "RFC822.SIZE", "FLAGS"]
    )

    # Sort messages by date in descending order
    sorted_messages = sorted(
        fetch_data.items(), key=lambda x: x[1][b"INTERNALDATE"], reverse=True
    )

    # Convert to EmailMetadata objects
    return [
        EmailMetadata.from_envelope_data(uid=uid, data=data)
        for uid, data in sorted_messages[:limit]
    ]
