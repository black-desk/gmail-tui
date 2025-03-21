"""List module for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import json
import sys
from enum import Enum, auto

import toml
import yaml

from gmail_tui.config import get_config
from gmail_tui.email import EmailMetadata
from gmail_tui.utils import connect_imap, fetch_email_metadata


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
        except KeyError:
            raise ValueError(f"Invalid format: {s}")


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


def list_emails(folder: str, limit: int = 20, output_format: str = "json") -> None:
    """List emails in a folder.

    Args:
        folder: Folder name to list emails from
        limit: Maximum number of emails to show
        output_format: Output format (json/yaml/toml)

    """
    try:
        # Parse output format
        fmt = OutputFormat.from_str(output_format)

        # Get configuration
        config = get_config()

        # Connect to IMAP server
        with connect_imap(username=config.email, password=config.app_password) as client:
            # Fetch email metadata
            emails = fetch_email_metadata(client, folder, limit)

            # Check if we got any emails
            if not emails:
                print(f"No emails found in folder: {folder}")
                return

            # Format and print output
            formatted_output = format_output(emails, fmt)
            print(formatted_output)
    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
