"""Threads command implementation.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

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


@dataclass
class EmailThread:
    """Represents an email thread (conversation)."""

    thread_id: str  # Root message ID
    email_count: int = 0
    latest_email_date: datetime | None = None
    participants: set[str] = field(default_factory=set)
    subject: str | None = None
    emails: list[EmailMetadata] = field(default_factory=list)

    def add_email(self, email: EmailMetadata) -> None:
        """Add an email to this thread.

        Args:
            email: Email metadata to add

        """
        self.emails.append(email)
        self.email_count = len(self.emails)

        # Update latest date
        if self.latest_email_date is None or email.internal_date > self.latest_email_date:
            self.latest_email_date = email.internal_date

        # Add participants
        if email.from_addr:
            # Extract email address from "Name <email>" format
            match = re.search(r"<([^<>]+)>", email.from_addr)
            if match:
                self.participants.add(match.group(1))
            elif "@" in email.from_addr:
                # No angle brackets, just an email address
                self.participants.add(email.from_addr)

        # Set subject from the root email (first email added)
        if self.subject is None and email.subject:
            self.subject = email.subject

    def to_dict(self) -> dict[str, Any]:
        """Convert thread to dictionary.

        Returns:
            Dictionary representation of the thread

        """
        return {
            "thread_id": self.thread_id,
            "email_count": self.email_count,
            "latest_email_date": self.latest_email_date.isoformat() if self.latest_email_date else None,
            "participants": sorted(list(self.participants)),
            "subject": self.subject,
            "email_uids": [email.uid for email in self.emails],
        }


def build_threads(emails: list[EmailMetadata]) -> list[EmailThread]:
    """Build threads from a list of emails.

    Args:
        emails: List of email metadata

    Returns:
        List of EmailThread objects sorted by latest email date

    """
    # Map message IDs to threads
    message_to_thread: dict[str, EmailThread] = {}

    # Map message IDs to their email metadata
    message_to_email: dict[str, EmailMetadata] = {
        normalize_message_id(email.message_id): email
        for email in emails
        if normalize_message_id(email.message_id)
    }

    for email in emails:
        message_id = normalize_message_id(email.message_id)
        if not message_id:
            continue

        in_reply_to = normalize_message_id(email.in_reply_to)
        references = parse_references(email.references)

        # Determine thread ID (parent message ID)
        # Default: email is a thread root
        thread_id = message_id
        thread = None

        # Check if this email is part of an existing thread
        if in_reply_to and in_reply_to in message_to_thread:
            # Direct reply to an existing message
            thread_id = in_reply_to
        elif in_reply_to and in_reply_to in message_to_email:
            # Direct reply to a message that exists but hasn't been processed yet
            # Create thread using the parent message ID as thread ID
            thread_id = in_reply_to
        elif references:
            # Check references in reverse order (most recent first)
            for ref_id in reversed(references):
                if ref_id in message_to_thread:
                    # Reference already has a thread
                    thread_id = ref_id
                    break
                elif ref_id in message_to_email:
                    # Reference exists but hasn't been processed yet
                    thread_id = ref_id
                    break

        # Get or create thread
        if thread_id in message_to_thread:
            thread = message_to_thread[thread_id]
        else:
            thread = EmailThread(thread_id=thread_id)
            message_to_thread[thread_id] = thread

        # Add email to thread
        thread.add_email(email)

        # Register this message ID if it's not already in the map
        # This allows future replies to find this thread
        if message_id not in message_to_thread:
            message_to_thread[message_id] = thread

    # Remove duplicates (same thread object may be registered with multiple keys)
    unique_threads = []
    seen = set()
    for thread in message_to_thread.values():
        if id(thread) not in seen:
            seen.add(id(thread))
            unique_threads.append(thread)

    # Sort threads by latest email date (descending)
    sorted_threads = sorted(
        unique_threads,
        key=lambda t: t.latest_email_date or datetime.min,
        reverse=True,
    )

    return sorted_threads


def format_output(threads: list[EmailThread], output_format: OutputFormat) -> str:
    """Format thread list in specified format.

    Args:
        threads: List of EmailThread objects
        output_format: Output format

    Returns:
        Formatted string

    """
    # Convert threads to list of dicts
    data = [thread.to_dict() for thread in threads]

    if output_format == OutputFormat.JSON:
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif output_format == OutputFormat.YAML:
        return yaml.dump(data, allow_unicode=True, sort_keys=False)
    elif output_format == OutputFormat.TOML:
        return toml.dumps({"threads": data})

    raise ValueError(f"Unsupported format: {output_format}")


def list_threads(folder: str, limit: int = 20, output_format: str = "json") -> None:
    """List email threads in a folder.

    Args:
        folder: Folder name to list threads from
        limit: Maximum number of threads to show
        output_format: Output format (json/yaml/toml)

    """
    try:
        # Parse output format
        fmt = OutputFormat.from_str(output_format)

        # Get configuration
        config = get_config()

        # Connect to IMAP server using connection manager
        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            # Fetch email metadata (fetch more to build threads properly)
            # We fetch more emails than limit to ensure we get complete threads
            fetch_limit = limit * 5  # Fetch more to build complete threads
            emails = fetch_email_metadata(client, folder, limit=fetch_limit)

            # Check if we got any emails
            if not emails:
                sys.stdout.write(f"No emails found in folder: {folder}\n")
                return

            # Build threads
            threads = build_threads(emails)

            # Apply limit
            threads = threads[:limit]

            # Check if we got any threads
            if not threads:
                sys.stdout.write(f"No threads found in folder: {folder}\n")
                return

            # Format and print output
            formatted_output = format_output(threads, fmt)
            sys.stdout.write(f"{formatted_output}\n")
    except ValueError as e:
        sys.stderr.write(f"Error: {e!s}\n")
    except Exception as e:
        sys.stderr.write(f"Error: {e!s}\n")
