"""Utility functions for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from .imap import (
    close_all_imap_connections,
    close_imap_connection,
    connect_imap,
    fetch_email_metadata,
    get_imap_connection,
    list_folders,
    list_folders_client,
)

__all__ = [
    "close_all_imap_connections",
    "close_imap_connection",
    "connect_imap",
    "fetch_email_metadata",
    "get_imap_connection",
    "list_folders",
    "list_folders_client",
]

__all__ = [
    "close_all_imap_connections",
    "close_imap_connection",
    "connect_imap",
    "fetch_email_metadata",
    "get_imap_connection",
    "list_folders",
    "list_folders_client",
]
