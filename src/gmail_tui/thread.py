"""Thread command implementation.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import email.message
import email.policy
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

import toml
import yaml

from gmail_tui.config import get_config
from gmail_tui.email import EmailMetadata
from gmail_tui.show import email_to_dict
from gmail_tui.utils import fetch_email_metadata, get_imap_connection


class OutputFormat(Enum):
    """Output format enum."""

    JSON = auto()
    YAML = auto()
    TOML = auto()

    @classmethod
    def from_str(cls, s: str) -> "OutputFormat":
        """Create OutputFormat from string.

        Args:
            s: Format string

        Returns:
            OutputFormat enum value

        Raises:
            ValueError: If format string is invalid

        """
        try:
            return {
                "json": cls.JSON,
                "yaml": cls.YAML,
                "toml": cls.TOML,
            }[s.lower()]
        except KeyError as err:
            raise ValueError(f"Invalid format: {s}") from err


def normalize_message_id(message_id: str | None) -> str | None:
    """Normalize a message ID by stripping angle brackets and whitespace.

    Args:
        message_id: Raw message ID string

    Returns:
        Normalized message ID or None

    """
    if not message_id:
        return None
    # Strip angle brackets and whitespace
    normalized = message_id.strip().strip("<>")
    return normalized if normalized else None


def parse_references(references: str | None) -> list[str]:
    """Parse the References header into a list of message IDs.

    Args:
        references: References header string

    Returns:
        List of normalized message IDs

    """
    if not references:
        return []
    # Message IDs in References header are separated by whitespace and/or angle brackets
    # Pattern matches message IDs inside angle brackets
    message_ids = re.findall(r"<([^<>]+)>", references)
    return message_ids


def find_thread_root(message_id: str, in_reply_to: str | None, references: str | None) -> str:
    """Find the thread root message ID.

    The thread root is the oldest message in the thread. We determine this by:
    1. Checking References header (which lists all ancestors from oldest to newest)
    2. If no References, check In-Reply-To (parent message)
    3. Otherwise, this message is the root

    Args:
        message_id: Current message ID
        in_reply_to: In-Reply-To header value
        references: References header value

    Returns:
        Thread root message ID

    """
    references_list = parse_references(references)
    if references_list:
        # References contains all ancestors, oldest first
        return references_list[0]

    in_reply_to_normalized = normalize_message_id(in_reply_to)
    if in_reply_to_normalized:
        return in_reply_to_normalized

    return message_id


def build_thread_from_emails(emails: list[EmailMetadata], target_message_id: str) -> tuple[str, list[EmailMetadata]]:
    """Build a thread from a list of emails containing the target message.

    Args:
        emails: List of email metadata
        target_message_id: The message ID to find the thread for

    Returns:
        Tuple of (thread_root_message_id, emails_in_thread)

    Raises:
        ValueError: If target message ID is not found in emails

    """
    # Build a map of message IDs to emails
    message_to_email: dict[str, EmailMetadata] = {
        normalize_message_id(email.message_id): email
        for email in emails
        if normalize_message_id(email.message_id)
    }

    # Build a map of all message IDs to their thread root
    message_to_root: dict[str, str] = {}

    # Find all message IDs that belong to threads
    for email in emails:
        message_id = normalize_message_id(email.message_id)
        if not message_id:
            continue

        root_id = find_thread_root(message_id, email.in_reply_to, email.references)
        message_to_root[message_id] = root_id

        # Also register all references pointing to this message
        references_list = parse_references(email.references)
        for ref_id in references_list:
            if ref_id not in message_to_root:
                message_to_root[ref_id] = root_id

    # Find the thread root for the target message
    target_id_normalized = normalize_message_id(target_message_id)
    if target_id_normalized not in message_to_root:
        # Check if the target message is in our email list
        if target_id_normalized not in message_to_email:
            raise ValueError(f"Message ID {target_id_normalized} not found in fetched emails")
        # Target message has no thread info, treat as standalone thread
        thread_root = target_id_normalized
    else:
        thread_root = message_to_root[target_id_normalized]

    # Collect all emails belonging to this thread
    thread_emails = [
        email for email in emails
        if normalize_message_id(email.message_id) in message_to_root
        and message_to_root[normalize_message_id(email.message_id)] == thread_root
    ]

    # Also include emails where this message is in their references
    for email in emails:
        message_id = normalize_message_id(email.message_id)
        if message_id and message_id not in message_to_root:
            # This email might reference the thread root or any email in the thread
            references_list = parse_references(email.references)
            for ref_id in references_list:
                if ref_id in message_to_root and message_to_root[ref_id] == thread_root:
                    if email not in thread_emails:
                        thread_emails.append(email)
                    message_to_root[message_id] = thread_root
                    break

    # Sort emails by date (ascending for thread order)
    thread_emails.sort(key=lambda e: e.internal_date or datetime.min)

    return thread_root, thread_emails


def fetch_full_email(client: Any, uid: int, folder: str) -> dict[str, Any]:
    """Fetch full email content.

    Args:
        client: IMAPClient object
        uid: Email UID
        folder: Folder to fetch from

    Returns:
        Dictionary representation of the email

    """
    client.select_folder(folder)

    # Fetch the full email
    fetch_data = client.fetch([uid], ["RFC822"])
    if uid not in fetch_data or b"RFC822" not in fetch_data[uid]:
        raise ValueError(f"Failed to fetch email with UID {uid}")

    # Create message object
    message = email.message_from_bytes(fetch_data[uid][b"RFC822"], policy=email.policy.default)

    # Convert to dictionary
    return email_to_dict(message, uid, include_headers=False)


def format_output(thread_root: str, emails: list[dict[str, Any]], output_format: OutputFormat) -> str:
    """Format thread output in specified format.

    Args:
        thread_root: Thread root message ID
        emails: List of email dictionaries
        output_format: Output format

    Returns:
        Formatted string

    """
    data = {
        "thread_root": thread_root,
        "email_count": len(emails),
        "emails": emails,
    }

    if output_format == OutputFormat.JSON:
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif output_format == OutputFormat.YAML:
        return yaml.dump(data, allow_unicode=True, sort_keys=False)
    elif output_format == OutputFormat.TOML:
        return toml.dumps({"thread": data})

    raise ValueError(f"Unsupported format: {output_format}")


def show_thread(message_id: str, folder: str = "INBOX", output_format: str = "json") -> None:
    """Display all emails in a thread.

    Args:
        message_id: Any message ID from the thread
        folder: Folder to search in (default: INBOX)
        output_format: Output format (json/yaml/toml)

    """
    try:
        # Parse output format
        fmt = OutputFormat.from_str(output_format)

        # Normalize the message ID
        target_message_id = normalize_message_id(message_id)
        if not target_message_id:
            sys.stderr.write("Error: Invalid message ID\n")
            return

        # Get configuration
        config = get_config()

        # Connect to IMAP server
        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            # Fetch email metadata from the folder
            # We need to fetch all emails to properly build threads
            emails = fetch_email_metadata(client, folder, limit=1000)

            if not emails:
                sys.stderr.write(f"No emails found in folder: {folder}\n")
                return

            # Build thread
            try:
                thread_root, thread_emails = build_thread_from_emails(emails, target_message_id)
            except ValueError as e:
                sys.stderr.write(f"Error: {e!s}\n")
                return

            if not thread_emails:
                sys.stderr.write(f"No emails found in thread for Message-ID: {target_message_id}\n")
                return

            # Fetch full content for each email in the thread
            full_emails = []
            for email_metadata in thread_emails:
                try:
                    email_dict = fetch_full_email(client, email_metadata.uid, folder)
                    full_emails.append(email_dict)
                except Exception as e:
                    sys.stderr.write(f"Warning: Failed to fetch email UID {email_metadata.uid}: {e!s}\n")

            # Format and print output
            formatted_output = format_output(thread_root, full_emails, fmt)
            sys.stdout.write(f"{formatted_output}\n")
    except ValueError as e:
        sys.stderr.write(f"Error: {e!s}\n")
    except Exception as e:
        sys.stderr.write(f"Error: {e!s}\n")
