"""Search command implementation.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import json
import re
import sys
from enum import Enum, auto

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


def format_output(emails: list[EmailMetadata], output_format: OutputFormat) -> str:
    """Format email metadata list in specified format.

    Args:
        emails: List of email metadata
        output_format: Output format

    Returns:
        Formatted string

    """
    # Convert emails to list of dicts
    data = [email.to_dict() for email in emails]

    if output_format == OutputFormat.JSON:
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif output_format == OutputFormat.YAML:
        return yaml.dump(data, allow_unicode=True, sort_keys=False)
    elif output_format == OutputFormat.TOML:
        return toml.dumps({"emails": data})

    raise ValueError(f"Unsupported format: {output_format}")


def search_emails(
    folder: str,
    limit: int = 20,
    output_format: str = "json",
    from_addr: str | None = None,
    to_addr: str | None = None,
    subject: str | None = None,
    body: str | None = None,
) -> None:
    """Search emails with various filters.

    Args:
        folder: Folder name to search in
        limit: Maximum number of emails to return
        output_format: Output format (json/yaml/toml)
        from_addr: Filter by sender
        to_addr: Filter by recipient
        subject: Filter by subject
        body: Search in email body

    """
    try:
        # Parse output format
        fmt = OutputFormat.from_str(output_format)

        # Get configuration
        config = get_config()

        # Build IMAP search criteria
        # Note: Greenmail doesn't support quoted strings in search, use simple format
        search_criteria = []
        if from_addr:
            search_criteria.extend(["FROM", from_addr])
        if to_addr:
            search_criteria.extend(["TO", to_addr])
        if subject:
            search_criteria.extend(["SUBJECT", subject])

        # Note: IMAP BODY search is not reliable across all servers
        # and doesn't support full text search. We'll fetch emails first
        # and filter by body content if needed.
        use_body_filter = body is not None

        # Connect to IMAP server using connection manager
        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            # Search emails
            emails = fetch_email_metadata(
                client, folder, limit=limit, search_criteria=search_criteria or None
            )

            # Filter by body content if requested
            if use_body_filter and emails:
                emails = filter_by_body(client, folder, emails, body)

            # Check if we got any emails
            if not emails:
                sys.stdout.write(f"No emails found matching criteria in folder: {folder}\n")
                return

            # Format and print output
            formatted_output = format_output(emails, fmt)
            sys.stdout.write(f"{formatted_output}\n")
    except ValueError as e:
        sys.stderr.write(f"Error: {e!s}\n")
    except Exception as e:
        sys.stderr.write(f"Error: {e!s}\n")


def filter_by_body(
    client, folder: str, emails: list[EmailMetadata], body_text: str
) -> list[EmailMetadata]:
    """Filter emails by body content.

    Args:
        client: IMAPClient object
        folder: Folder name
        emails: List of email metadata to filter
        body_text: Text to search for in email body

    Returns:
        Filtered list of emails

    """
    # Compile case-insensitive regex for body search
    body_regex = re.compile(re.escape(body_text), re.IGNORECASE)
    filtered = []

    # Fetch full email content for each email and check body
    for email in emails:
        try:
            message = email.fetch_full_email(client, folder)
            if message_contains_text(message, body_regex):
                filtered.append(email)
        except Exception:
            # Skip emails that fail to fetch
            continue

    return filtered


def message_contains_text(message, pattern: re.Pattern) -> bool:
    """Check if an email message contains the given pattern in its body.

    Args:
        message: Email message object
        pattern: Compiled regex pattern to search for

    Returns:
        True if pattern found in message body, False otherwise

    """
    # Walk through all parts of the message
    for part in message.walk():
        # Skip non-text parts
        if part.get_content_type() not in ("text/plain", "text/html"):
            continue

        # Decode and search the payload
        try:
            payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                # Try to decode with common encodings
                for encoding in ["utf-8", "latin1", "cp1252"]:
                    try:
                        text = payload.decode(encoding)
                        if pattern.search(text):
                            return True
                        break
                    except UnicodeDecodeError:
                        continue
            else:
                text = str(payload)
                if pattern.search(text):
                    return True
        except Exception:
            # Skip parts that fail to decode
            continue

    return False
