"""Utility functions for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black_desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from .imap import connect_imap, fetch_email_metadata

__all__ = ["connect_imap", "fetch_email_metadata"]
