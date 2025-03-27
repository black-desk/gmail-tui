"""Main entry point for Gmail TUI.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import argparse
import sys

from .app import main as app_main
from .config.init import init_config


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Gmail TUI - A terminal user interface for Gmail")
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize configuration file",
    )
    args = parser.parse_args()

    if args.init:
        init_config()
        sys.exit(0)

    app_main()


if __name__ == "__main__":
    main()
