"""Action definitions for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from enum import Enum, auto


class Action(str, Enum):
    """Available actions in Gmail TUI."""

    QUIT = "quit"
    REFRESH = "refresh"
    NEXT = "next"
    PREVIOUS = "previous"
    TOP = "top"
    BOTTOM = "bottom"
    OPEN = "open"
    DELETE = "delete"
    ARCHIVE = "archive"
    STAR = "star"
    MARK_READ = "mark_read"
    SEARCH = "search"
    NEXT_RESULT = "next_result"
    PREVIOUS_RESULT = "previous_result"
    HELP = "help"


ACTION_DESCRIPTIONS: dict[Action, str] = {
    Action.QUIT: "Quit",
    Action.REFRESH: "Refresh",
    Action.NEXT: "Next item",
    Action.PREVIOUS: "Previous item",
    Action.TOP: "Go to top",
    Action.BOTTOM: "Go to bottom",
    Action.OPEN: "Open email",
    Action.DELETE: "Delete email",
    Action.ARCHIVE: "Archive email",
    Action.STAR: "Star/Unstar email",
    Action.MARK_READ: "Mark as read/unread",
    Action.SEARCH: "Search emails",
    Action.NEXT_RESULT: "Next search result",
    Action.PREVIOUS_RESULT: "Previous search result",
    Action.HELP: "Show help",
} 