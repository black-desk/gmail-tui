"""IMAP utilities for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import logging
from typing import Any

from imapclient import IMAPClient

from gmail_tui.email import EmailMetadata

# Configure logger
logger = logging.getLogger(__name__)

# Global connection pool to reuse IMAP connections
# Key: (username, password), Value: IMAPClient instance
_imap_connections: dict[tuple[str, str], IMAPClient] = {}


class IMAPConnectionManager:
    """Context manager wrapper for IMAPClient connections from the pool."""

    def __init__(self, username: str, password: str):
        """Initialize the connection manager.

        Args:
            username: Gmail address
            password: App password for Gmail

        """
        self.username = username
        self.password = password
        self.client = None

    def __enter__(self) -> IMAPClient:
        """Enter the context and return a client connection.

        Returns:
            IMAPClient: An IMAP client connection from the pool

        """
        self.client = connect_imap(self.username, self.password)
        return self.client

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context without closing the connection."""
        # We don't logout here, as connections are managed by the pool
        # Note: The connection remains in the pool for future use
        pass


def connect_imap(username: str, password: str) -> IMAPClient:
    """Connect to Gmail IMAP server.

    Args:
        username: Gmail address
        password: App password for Gmail

    Returns:
        IMAPClient object

    """
    # Check if connection exists in the pool
    connection_key = (username, password)
    if connection_key in _imap_connections:
        client = _imap_connections[connection_key]
        # Check if the connection is still alive
        try:
            # Perform a simple operation to check connection
            client.noop()
            return client
        except Exception:
            # Connection is dead, remove it from the pool
            del _imap_connections[connection_key]

    # Create new connection
    client = IMAPClient("imap.gmail.com")
    client.login(username, password)

    # Store in connection pool
    _imap_connections[connection_key] = client
    return client


def get_imap_connection(username: str, password: str) -> IMAPConnectionManager:
    """Get an IMAP connection for use with a context manager.

    Args:
        username: Gmail address
        password: App password for Gmail

    Returns:
        IMAPConnectionManager context manager

    """
    return IMAPConnectionManager(username, password)


def close_imap_connection(username: str, password: str) -> None:
    """Close and remove an IMAP connection from the pool.

    Args:
        username: Gmail address
        password: App password for Gmail

    """
    connection_key = (username, password)
    if connection_key in _imap_connections:
        try:
            _imap_connections[connection_key].logout()
        except Exception as e:
            # Log but ignore errors during logout
            # This is intentional as we're cleaning up resources
            logger.debug(f"Error during IMAP logout (ignored): {e}")
        del _imap_connections[connection_key]


def close_all_imap_connections() -> None:
    """Close all IMAP connections in the pool."""
    for client in _imap_connections.values():
        try:
            client.logout()
        except Exception as e:
            # Log but ignore errors during logout
            # This is intentional as we're cleaning up resources
            logger.debug(f"Error during IMAP logout (ignored): {e}")
    _imap_connections.clear()


def fetch_email_metadata(
    client: IMAPClient,
    folder: str,
    limit: int = 20,
    search_criteria: list[str] | None = None,
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
