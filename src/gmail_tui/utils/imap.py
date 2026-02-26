"""IMAP utilities for Gmail TUI.

SPDX-FileCopyrightText: 2024-2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import email.message
import email.utils
import imaplib
import logging
from datetime import datetime
from typing import Any

from gmail_tui.email import EmailMetadata, decode_mime_words

# Configure logger
logger = logging.getLogger(__name__)

# Global connection pool to reuse IMAP connections
# Key: (username, password), Value: imaplib.IMAP4 instance
_imap_connections: dict[tuple[str, str], imaplib.IMAP4] = {}


class IMAPConnectionManager:
    """Context manager wrapper for IMAP4 connections from pool."""

    def __init__(self, username: str, password: str):
        """Initialize connection manager.

        Args:
            username: Gmail address
            password: App password for Gmail

        """
        self.username = username
        self.password = password
        self.client = None

    def __enter__(self) -> imaplib.IMAP4:
        """Enter context and return a client connection.

        Returns:
            imaplib.IMAP4: An IMAP4 client connection from pool

        """
        self.client = connect_imap(self.username, self.password)
        return self.client

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context without closing connection."""
        # We don't logout here, as connections are managed by the pool
        # Note: The connection remains in the pool for future use
        pass


def connect_imap(username: str, password: str) -> imaplib.IMAP4:
    """Connect to IMAP server.

    Args:
        username: Gmail address
        password: App password for Gmail

    Returns:
        imaplib.IMAP4 object

    """
    from gmail_tui.config import get_config

    config = get_config()

    # Check if connection exists in pool
    connection_key = (username, password)
    if connection_key in _imap_connections:
        client = _imap_connections[connection_key]
        # Check if connection is still alive
        try:
            # Perform a simple operation to check connection
            client.noop()
            return client
        except Exception:
            # Connection is dead, remove it from pool
            del _imap_connections[connection_key]

    # Create new connection
    if config.imap_ssl:
        client = imaplib.IMAP4_SSL(host=config.imap_server, port=config.imap_port)
    else:
        client = imaplib.IMAP4(host=config.imap_server, port=config.imap_port)

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
    client: imaplib.IMAP4,
    folder: str,
    limit: int = 20,
    login: bool = True,
) -> list[EmailMetadata]:
    """Fetch email metadata from IMAP server.

    Args:
        client: IMAP4 object
        folder: Folder name to fetch emails from
        limit: Maximum number of emails to fetch
        login: Whether to perform login (False for smtp4dev)

    Returns:
        List of EmailMetadata objects

    """
    # Login if required (for servers that need authentication after initial login)
    if login:
        # Check if already authenticated
        try:
            client.noop()
        except Exception:
            # Try to get username/password from connection pool key
            from gmail_tui.config import get_config
            config = get_config()
            client.login(config.email, config.app_password)

    # Select folder
    typ, _ = client.select(folder)
    if typ != "OK":
        logger.warning(f"Failed to select folder: {folder}")
        return []

    # Search for all messages
    typ, data = client.search(None, "ALL")
    if typ != "OK":
        logger.warning("Failed to search for messages")
        return []

    # Parse message IDs
    msg_ids = data[0].split() if data[0] else []
    if not msg_ids:
        return []

    # Take most recent messages (highest IDs first, IMAP uses sequence numbers)
    # Note: These are message sequence numbers, not UIDs
    seq_ids = sorted([int(id) for id in msg_ids], reverse=True)[:limit]

    result = []
    for seq_id in seq_ids:
        # Fetch internal date and RFC822.HEADER (no need to fetch full body)
        typ, data = client.fetch(str(seq_id), "(INTERNALDATE RFC822.HEADER)")
        if typ != "OK" or not data:
            continue

        # Parse the response - format can be either:
        # [(b'1 (INTERNALDATE "date" RFC822.HEADER {size})', b'header...')]
        # or [tuple, bytes] where tuple contains the metadata
        try:
            internal_date = None
            header_data = None

            for item in data:
                # Handle the tuple + bytes format
                if isinstance(item, tuple):
                    # Parse metadata from tuple, get header_data from second element
                    # Example: (b'4 (INTERNALDATE "date" RFC822.HEADER {size})', b'header...')
                    if len(item) >= 2:
                        for part in item:
                            if isinstance(part, bytes):
                                if b'INTERNALDATE' in part:
                                    try:
                                        start = part.find(b'"') + 1
                                        end = part.find(b'"', start)
                                        if start > 0 and end > start:
                                            date_str = part[start:end].decode()
                                            internal_date = email.utils.parsedate_to_datetime(date_str)
                                    except Exception:
                                        pass
                                # Second element is likely the header data
                                if not header_data and b'INTERNALDATE' not in part and part.strip():
                                    header_data = part
                elif isinstance(item, bytes) and not header_data:
                    # Handle standalone bytes format (this is the header data)
                    # Skip if it's just a closing paren
                    if item != b')':
                        header_data = item.lstrip()

            if not header_data:
                continue

            # Parse email from header data
            msg = email.message_from_bytes(header_data)

            # Create EmailMetadata using from_message method
            metadata = EmailMetadata.from_message(
                uid=seq_id,
                internal_date=internal_date or datetime.now(),
                message=msg,
                size=len(header_data),
            )

            result.append(metadata)

        except Exception as e:
            logger.warning(f"Failed to parse message {seq_id}: {e}")
            continue

    return result


def list_folders(client: imaplib.IMAP4) -> list[tuple[list[bytes], bytes, bytes]]:
    """List all folders in the mailbox.

    Args:
        client: IMAP4 object

    Returns:
        List of folder tuples (flags, delimiter, name)

    """
    # List command returns: (typ, [data])
    # Some IMAP servers return: ('OK', [b'(flags) "/" "name"', ...])
    # Others return: ('OK', [b'count', [b'(flags) "/" "name"', ...]])
    typ, data = client.list()
    if typ != "OK":
        raise RuntimeError(f"Failed to list folders: {typ}")

    folders = []
    # Process each folder entry
    for folder_data in data:
        if isinstance(folder_data, bytes):
            # Parse bytes format: b'(\\HasNoChildren) "/" "INBOX"'
            # Split by spaces to get parts
            parts = folder_data.split(b' ')
            if len(parts) >= 3:
                flags_part = parts[0]
                delimiter_part = parts[1].strip(b'"')
                name_part = parts[2].strip(b'"')
                # Parse flags
                flags = []
                if flags_part.startswith(b'(') and flags_part.endswith(b')'):
                    flags_str = flags_part[1:-1].strip()
                    if flags_str:
                        # Split by backslash if needed
                        if b'\\' in flags_str:
                            flags = [f.strip() for f in flags_str.split(b'\\') if f.strip()]
                        else:
                            flags = [flags_part]
                folders.append((flags, delimiter_part, name_part))
        elif isinstance(folder_data, (tuple, list)) and len(folder_data) >= 3:
            folders.append((folder_data[0], folder_data[1], folder_data[2]))

    return folders


def list_folders_client(client: imaplib.IMAP4) -> list[tuple[list[bytes], bytes, bytes]]:
    """List all folders - compatibility wrapper.

    Args:
        client: IMAP4 object (for backward compatibility)

    Returns:
        List of folder tuples (flags, delimiter, name)

    """
    return list_folders(client)
