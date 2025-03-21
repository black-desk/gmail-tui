"""Email module for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black_desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import email.message
from dataclasses import dataclass, field
from datetime import datetime
from email.header import decode_header
from typing import Any, Optional

from imapclient import IMAPClient


def decode_mime_words(s: Optional[str]) -> str:
    """Decode MIME encoded-word strings.

    Args:
        s: String to decode

    Returns:
        Decoded string

    """
    if not s:
        return ""
    result = []
    for decoded_str, charset in decode_header(s):
        if isinstance(decoded_str, bytes):
            if charset:
                result.append(decoded_str.decode(charset))
            else:
                result.append(decoded_str.decode())
        else:
            result.append(decoded_str)
    return "".join(result)


def format_address_list(addresses: Optional[list[Any]]) -> Optional[str]:
    """Format a list of email addresses from ENVELOPE format.

    Args:
        addresses: List of address objects or tuples

    Returns:
        Formatted email address string or None if empty

    """
    if not addresses:
        return None

    result = []
    for address in addresses:
        # Handle different address formats
        if (
            hasattr(address, "name")
            and hasattr(address, "mailbox")
            and hasattr(address, "host")
        ):
            # Process Address objects
            name = address.name
            mailbox = address.mailbox
            host = address.host
        elif isinstance(address, (list, tuple)) and len(address) >= 4:
            # Process tuple format (name, host_route, mailbox, host)
            name, _, mailbox, host = address
        else:
            # Skip unrecognized address formats
            continue

        parts = []
        if name:
            decoded_name = decode_mime_words(
                name.decode() if isinstance(name, bytes) else str(name)
            )
            if " " in decoded_name:
                parts.append(f'"{decoded_name}"')
            else:
                parts.append(decoded_name)

        email_address = ""
        if mailbox and host:
            mb = mailbox.decode() if isinstance(mailbox, bytes) else mailbox
            h = host.decode() if isinstance(host, bytes) else host
            email_address = f"{mb}@{h}"
            parts.append(f"<{email_address}>")
        elif mailbox:
            email_address = mailbox.decode() if isinstance(mailbox, bytes) else mailbox
            parts.append(f"<{email_address}>")

        if parts:
            result.append(" ".join(parts))

    return ", ".join(result) if result else None


@dataclass
class EmailMetadata:
    """Email metadata class."""

    uid: int
    internal_date: datetime
    subject: Optional[str] = None
    from_addr: Optional[str] = None
    to_addr: Optional[str] = None
    cc_addr: Optional[str] = None
    bcc_addr: Optional[str] = None
    date: Optional[str] = None
    message_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    references: Optional[str] = None
    content_type: Optional[str] = None
    content_disposition: Optional[str] = None
    size: int = 0
    flags: list[str] = field(default_factory=list)

    @classmethod
    def from_imap_data(cls, uid: int, data: dict) -> "EmailMetadata":
        """Create EmailMetadata from IMAP data with RFC822.

        Args:
            uid: Message UID
            data: IMAP data containing RFC822 and INTERNALDATE

        Returns:
            EmailMetadata object

        """
        message = email.message_from_bytes(data[b"RFC822"])
        return cls.from_message(
            uid=uid,
            internal_date=data[b"INTERNALDATE"],
            message=message,
            size=len(data[b"RFC822"]),
            flags=data.get(b"FLAGS", []),
        )

    @classmethod
    def from_message(
        cls,
        uid: int,
        internal_date: datetime,
        message: email.message.Message,
        size: int,
        flags: Optional[list[Any]] = None,
    ) -> "EmailMetadata":
        """Create EmailMetadata from an email message.

        Args:
            uid: Message UID
            internal_date: Internal date from IMAP
            message: Email message object
            size: Size of the message in bytes
            flags: Message flags

        Returns:
            EmailMetadata object

        """
        metadata = cls(uid=uid, internal_date=internal_date, size=size)
        if flags:
            metadata.flags = [
                flag.decode() if isinstance(flag, bytes) else str(flag)
                for flag in flags
            ]

        # Basic fields
        if message["subject"]:
            metadata.subject = decode_mime_words(message["subject"])
        if message["from"]:
            metadata.from_addr = decode_mime_words(message["from"])
        if message["to"]:
            metadata.to_addr = decode_mime_words(message["to"])
        if message["date"]:
            metadata.date = message["date"]

        # Optional fields
        if message["cc"]:
            metadata.cc_addr = decode_mime_words(message["cc"])
        if message["bcc"]:
            metadata.bcc_addr = decode_mime_words(message["bcc"])
        if message["message-id"]:
            metadata.message_id = message["message-id"]
        if message["in-reply-to"]:
            metadata.in_reply_to = message["in-reply-to"]
        if message["references"]:
            metadata.references = message["references"]

        # Content-related fields
        metadata.content_type = message.get_content_type()
        metadata.content_disposition = message.get_content_disposition()

        return metadata

    @classmethod
    def from_envelope_data(cls, uid: int, data: dict) -> "EmailMetadata":
        """Create EmailMetadata from IMAP ENVELOPE data.

        Args:
            uid: Message UID
            data: IMAP data containing ENVELOPE, INTERNALDATE and RFC822.SIZE

        Returns:
            EmailMetadata object

        """
        envelope = data[b"ENVELOPE"]
        size = data[b"RFC822.SIZE"]
        internal_date = data[b"INTERNALDATE"]
        flags = data.get(b"FLAGS", [])

        # Create metadata-only object
        metadata = cls(
            uid=uid,
            internal_date=internal_date,
            size=size,
            flags=[
                flag.decode() if isinstance(flag, bytes) else str(flag)
                for flag in flags
            ],
        )

        # Process email headers
        if envelope.subject:
            metadata.subject = decode_mime_words(
                envelope.subject.decode()
                if isinstance(envelope.subject, bytes)
                else str(envelope.subject)
            )

        # Process sender, recipients, etc.
        metadata.from_addr = format_address_list(envelope.from_)
        metadata.to_addr = format_address_list(envelope.to)
        metadata.cc_addr = format_address_list(envelope.cc)
        metadata.bcc_addr = format_address_list(envelope.bcc)

        # Process date and message ID
        if envelope.date:
            metadata.date = (
                envelope.date.decode()
                if isinstance(envelope.date, bytes)
                else str(envelope.date)
            )

        if envelope.message_id:
            metadata.message_id = (
                envelope.message_id.decode()
                if isinstance(envelope.message_id, bytes)
                else str(envelope.message_id)
            )

        if envelope.in_reply_to:
            metadata.in_reply_to = (
                envelope.in_reply_to.decode()
                if isinstance(envelope.in_reply_to, bytes)
                else str(envelope.in_reply_to)
            )

        return metadata

    def fetch_full_email(
        self, client: IMAPClient, folder: Optional[str] = None
    ) -> email.message.Message:
        """Fetch the full email content when needed.

        Args:
            client: IMAPClient object
            folder: Folder containing the email (if None, uses current selected folder)

        Returns:
            Email message object

        """
        if folder:
            client.select_folder(folder)

        data = client.fetch([self.uid], ["RFC822"])[self.uid]
        return email.message_from_bytes(data[b"RFC822"])

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary containing email metadata

        """
        return {
            k: v
            for k, v in {
                "uid": self.uid,
                "internal_date": self.internal_date.isoformat(),
                "subject": self.subject,
                "from": self.from_addr,
                "to": self.to_addr,
                "cc": self.cc_addr,
                "bcc": self.bcc_addr,
                "date": self.date,
                "message_id": self.message_id,
                "in_reply_to": self.in_reply_to,
                "references": self.references,
                "content_type": self.content_type,
                "content_disposition": self.content_disposition,
                "size": self.size,
                "flags": self.flags,
            }.items()
            if v is not None
        }
