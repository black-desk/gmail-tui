"""Email list widget for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black_desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from typing import ClassVar

from textual import on, work
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable

from gmail_tui.email import EmailMetadata
from gmail_tui.utils.imap import connect_imap, fetch_email_metadata

# Constants for display formatting
MAX_SENDER_LENGTH = 30
MAX_SUBJECT_LENGTH = 70
TRUNCATED_SENDER_LENGTH = 27
TRUNCATED_SUBJECT_LENGTH = 67


class EmailList(Widget):
    """A widget that displays email list in a folder."""

    DEFAULT_CSS = """
    EmailList {
        height: 100%;
        border: round $primary;
        padding: 0 1;
    }

    DataTable {
        height: 100%;
        max-width: 100%;
    }
    """

    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("r", "refresh_emails", "Refresh email list"),
    ]

    class EmailSelected(Message):
        """Message sent when an email is selected."""

        def __init__(self, email: EmailMetadata) -> None:
            """Initialize the message.

            Args:
                email: Selected email metadata

            """
            self.email = email
            super().__init__()

    class EmailsUpdated(Message):
        """Message sent when emails are updated."""

        def __init__(self, emails: list[EmailMetadata]) -> None:
            """Initialize the message.

            Args:
                emails: List of email metadata

            """
            self.emails = emails
            super().__init__()

    def __init__(self) -> None:
        """Initialize the email list widget."""
        super().__init__()
        self.table = DataTable(zebra_stripes=True, cursor_type="row")
        self.current_folder: str = ""
        self.email: str = ""
        self.app_password: str = ""
        self.emails: list[EmailMetadata] = []

    def set_credentials(self, email: str, app_password: str) -> None:
        """Set IMAP credentials.

        Args:
            email: Gmail address
            app_password: App password for Gmail

        """
        self.email = email
        self.app_password = app_password

    def set_folder(self, folder: str) -> None:
        """Set current folder.

        Args:
            folder: Folder path

        """
        self.current_folder = folder
        self.action_refresh_emails()

    def compose(self) -> ComposeResult:
        """Compose the widget's child widgets.

        Returns:
            Iterator of child widgets

        """
        self.table.add_columns("From", "Subject")
        yield self.table

    def update_emails(self, emails: list[EmailMetadata]) -> None:
        """Update the email list with new data.

        Args:
            emails: List of email metadata

        """
        # Clear existing rows but keep columns
        self.table.clear()

        # Add rows
        for email in emails:
            sender = email.from_addr or "Unknown"
            subject = email.subject or "(No Subject)"

            # Adjust display format to prevent overflow
            if len(sender) > MAX_SENDER_LENGTH:
                sender = sender[:TRUNCATED_SENDER_LENGTH] + "..."

            if len(subject) > MAX_SUBJECT_LENGTH:
                subject = subject[:TRUNCATED_SUBJECT_LENGTH] + "..."

            self.table.add_row(sender, subject)

    @on(DataTable.RowSelected)
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection events.

        Args:
            event: Row selection event

        """
        if not self.emails or event.cursor_row >= len(self.emails):
            return

        # Get selected email
        email = self.emails[event.cursor_row]

        # Post email selected message
        self.post_message(self.EmailSelected(email))

    @on(EmailsUpdated)
    def on_emails_updated(self, message: EmailsUpdated) -> None:
        """Handle emails updated message.

        Args:
            message: Emails updated message

        """
        self.emails = message.emails
        self.update_emails(message.emails)

    @work(thread=True)
    def action_refresh_emails(self) -> None:
        """Refresh email list action."""
        if not self.email or not self.app_password or not self.current_folder:
            return

        # Connect to IMAP server - connection will be reused from pool if available
        client = connect_imap(username=self.email, password=self.app_password)

        try:
            # Get email list
            emails = fetch_email_metadata(client, self.current_folder)

            # Post update message
            self.post_message(self.EmailsUpdated(emails))
        except Exception:
            # No need to close the connection as it's managed by the connection pool
            raise

    @work(thread=True)
    def action_refresh(self) -> None:
        """Refresh action for the app-wide refresh command."""
        self.action_refresh_emails()

    def on_mount(self) -> None:
        """Handle widget mount event."""
        # If we have credentials and folder, refresh emails
        if self.email and self.app_password and self.current_folder:
            self.action_refresh_emails()
