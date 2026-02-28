"""Show command implementation.

SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import email.message
import email.policy
import json
import re
import sys
from enum import Enum, auto
from typing import Any

import toml
import yaml

from gmail_tui.config import get_config
from gmail_tui.email import EmailMetadata
from gmail_tui.utils import get_imap_connection


class OutputFormat(Enum):
    """Output format enum."""

    JSON = auto()
    YAML = auto()
    TOML = auto()
    RAW = auto()

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
                "raw": cls.RAW,
            }[s.lower()]
        except KeyError as err:
            raise ValueError(f"Invalid format: {s}") from err


def extract_email_body(message: email.message.Message) -> dict[str, Any]:
    """Extract email body content from message.

    Args:
        message: Email message object

    Returns:
        Dictionary containing body content with content type and text

    """
    bodies = {}

    # Try to get plain text body first
    plain_text = message.get_body(preferencelist=("plain",))
    if plain_text:
        body_content = plain_text.get_content()
        if isinstance(body_content, bytes):
            charset = plain_text.get_content_charset() or "utf-8"
            try:
                body_content = body_content.decode(charset)
            except UnicodeDecodeError:
                # Fallback to utf-8 with error handling
                body_content = body_content.decode("utf-8", errors="replace")
        bodies["plain"] = {
            "content_type": plain_text.get_content_type(),
            "text": body_content,
        }

    # Try to get HTML body
    html_body = message.get_body(preferencelist=("html",))
    if html_body:
        body_content = html_body.get_content()
        if isinstance(body_content, bytes):
            charset = html_body.get_content_charset() or "utf-8"
            try:
                body_content = body_content.decode(charset)
            except UnicodeDecodeError:
                body_content = body_content.decode("utf-8", errors="replace")
        bodies["html"] = {
            "content_type": html_body.get_content_type(),
            "text": body_content,
        }

    # If no structured body found, try to get payload directly
    if not bodies:
        payload = message.get_payload()
        if isinstance(payload, str):
            bodies["text"] = {
                "content_type": message.get_content_type(),
                "text": payload,
            }
        elif isinstance(payload, list) and len(payload) > 0:
            # multipart message without get_body support
            for part in payload:
                if isinstance(part, email.message.Message):
                    content_type = part.get_content_type()
                    content = part.get_content()
                    if isinstance(content, bytes):
                        charset = part.get_content_charset() or "utf-8"
                        try:
                            content = content.decode(charset)
                        except UnicodeDecodeError:
                            content = content.decode("utf-8", errors="replace")
                    if "text" in content_type:
                        if content_type == "text/plain" and "plain" not in bodies:
                            bodies["plain"] = {
                                "content_type": content_type,
                                "text": content,
                            }
                        elif content_type == "text/html" and "html" not in bodies:
                            bodies["html"] = {
                                "content_type": content_type,
                                "text": content,
                            }

    return bodies


def email_to_dict(
    message: email.message.Message,
    uid: int | None = None,
    include_headers: bool = False,
) -> dict[str, Any]:
    """Convert email message to dictionary representation.

    Args:
        message: Email message object
        uid: Message UID (optional)
        include_headers: Whether to include all headers

    Returns:
        Dictionary representation of the email

    """
    result: dict[str, Any] = {}

    if uid is not None:
        result["uid"] = uid

    # Basic headers
    for header in ["subject", "from", "to", "cc", "bcc", "date", "message-id"]:
        value = message[header]
        if value:
            key = header.replace("-", "_")
            result[key] = value

    # Optional headers
    for header in ["in-reply-to", "references", "reply-to", "sender"]:
        value = message[header]
        if value:
            key = header.replace("-", "_")
            result[key] = value

    # Content info
    result["content_type"] = message.get_content_type()
    result["content_disposition"] = message.get_content_disposition()

    # All headers if requested
    if include_headers:
        headers = {}
        for key, value in message.items():
            if value:
                headers[key.lower()] = value
        result["headers"] = headers

    # Extract body
    bodies = extract_email_body(message)
    if bodies:
        result["body"] = bodies

    return result


def parse_identifier(id_str: str) -> tuple[bool, str]:
    """Parse email identifier to determine type.

    Args:
        id_str: Email identifier string

    Returns:
        Tuple of (is_uid, identifier)
        - is_uid: True if the identifier is a numeric UID
        - identifier: The parsed identifier

    """
    # Check if it looks like a numeric UID
    if id_str.strip().isdigit():
        return True, id_str.strip()

    # It's a message-id (might be wrapped in angle brackets)
    message_id = id_str.strip()
    if message_id.startswith("<") and message_id.endswith(">"):
        message_id = message_id[1:-1]

    return False, message_id


def find_email_by_message_id(
    client: Any, folder: str, message_id: str
) -> tuple[int | None, dict[str, Any] | None]:
    """Find an email by its message-id in a folder.

    Args:
        client: IMAPClient object
        folder: Folder to search in
        message_id: Message-ID header value (without angle brackets)

    Returns:
        Tuple of (uid, fetch_data) or (None, None) if not found

    """
    client.select_folder(folder)

    # Search for messages with the given message-id
    # Note: The search criteria format for HEADER is "HEADER field-name value"
    # We need to escape the message-id properly
    messages = client.search([f'HEADER Message-ID "<{message_id}>"'])

    if not messages:
        return None, None

    # Take the first match
    uid = messages[0]

    # Fetch the email
    fetch_data = client.fetch([uid], ["ENVELOPE", "INTERNALDATE", "RFC822.SIZE"])
    if uid not in fetch_data:
        return None, None

    return uid, fetch_data[uid]


def show_email(
    identifier: str,
    folder: str = "INBOX",
    output_format: str = "raw",
    include_headers: bool = False,
) -> None:
    """Display full email content.

    Args:
        identifier: Email identifier (uid or message-id)
        folder: Folder containing the email
        output_format: Output format (json/yaml/toml/raw)
        include_headers: Whether to include all headers

    """
    try:
        # Parse output format
        fmt = OutputFormat.from_str(output_format)

        # Parse identifier
        is_uid, parsed_id = parse_identifier(identifier)

        # Get configuration
        config = get_config()

        # Connect to IMAP server
        with get_imap_connection(
            username=config.email, password=config.app_password
        ) as client:
            uid = None
            message = None

            if is_uid:
                # Direct UID lookup
                uid = int(parsed_id)
                client.select_folder(folder)

                # Check if UID exists
                uids = client.search(["ALL"])
                if uid not in uids:
                    sys.stderr.write(f"Error: Email with UID {uid} not found in folder {folder}\n")
                    return

                # Fetch the full email
                fetch_data = client.fetch([uid], ["RFC822"])
                if uid not in fetch_data or b"RFC822" not in fetch_data[uid]:
                    sys.stderr.write(f"Error: Failed to fetch email with UID {uid}\n")
                    return

                # Create message object using EmailMessage class for get_body support
                message = email.message_from_bytes(fetch_data[uid][b"RFC822"], policy=email.policy.default)
            else:
                # Message-ID lookup
                message_id = parsed_id
                uid, _ = find_email_by_message_id(client, folder, message_id)

                if uid is None:
                    sys.stderr.write(
                        f"Error: Email with Message-ID <{message_id}> not found in folder {folder}\n"
                    )
                    return

                # Fetch the full email
                fetch_data = client.fetch([uid], ["RFC822"])
                if uid not in fetch_data or b"RFC822" not in fetch_data[uid]:
                    sys.stderr.write(f"Error: Failed to fetch email with Message-ID <{message_id}>\n")
                    return

                # Create message object using EmailMessage class for get_body support
                message = email.message_from_bytes(fetch_data[uid][b"RFC822"], policy=email.policy.default)

            # Format and output
            if fmt == OutputFormat.RAW:
                # Use email.policy.SMTP to properly format the raw email
                raw_output = message.as_bytes(policy=email.policy.SMTP).decode("utf-8", errors="replace")
                sys.stdout.write(raw_output)
            else:
                # Convert to dict for structured output
                email_dict = email_to_dict(message, uid, include_headers)

                if fmt == OutputFormat.JSON:
                    sys.stdout.write(json.dumps(email_dict, indent=2, ensure_ascii=False) + "\n")
                elif fmt == OutputFormat.YAML:
                    sys.stdout.write(yaml.dump(email_dict, allow_unicode=True, sort_keys=False))
                elif fmt == OutputFormat.TOML:
                    sys.stdout.write(toml.dumps({"email": email_dict}))
                else:
                    raise ValueError(f"Unsupported format: {fmt}")

    except ValueError as e:
        sys.stderr.write(f"Error: {e!s}\n")
    except Exception as e:
        sys.stderr.write(f"Error: {e!s}\n")
