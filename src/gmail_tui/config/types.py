"""Type definitions for Gmail TUI configuration.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from typing import NamedTuple


class ActionInfo(NamedTuple):
    """Action information."""

    name: str
    description: str 