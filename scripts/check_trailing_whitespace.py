#!/usr/bin/env python3
"""Script to check for and remove trailing whitespace in text files.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

import argparse
import re
import sys
from pathlib import Path


def find_text_files(directory: Path, extensions: list[str]) -> list[Path]:
    """Find all text files with given extensions in directory.

    Args:
        directory: Directory to search in
        extensions: List of file extensions to include

    Returns:
        List of paths to text files

    """
    result = []

    # Handle specific extensions first
    for ext in extensions:
        for file_path in directory.glob(f"**/*{ext}"):
            if file_path.is_file():
                result.append(file_path)

    return result


def check_file_for_trailing_whitespace(file_path: Path) -> list[tuple[int, str]]:
    """Check a file for trailing whitespace.

    Args:
        file_path: Path to the file to check

    Returns:
        List of (line_number, line_content) pairs with trailing whitespace

    """
    trailing_whitespace_pattern = re.compile(r'[ \t]+$')
    results = []

    try:
        with file_path.open(encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if trailing_whitespace_pattern.search(line):
                    results.append((line_num, line.rstrip('\n')))
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)  # noqa: T201

    return results


def remove_trailing_whitespace(file_path: Path) -> int:
    """Remove trailing whitespace from a file.

    Args:
        file_path: Path to the file to modify

    Returns:
        Number of lines modified

    """
    trailing_whitespace_pattern = re.compile(r'[ \t]+$')
    modified_lines = 0

    try:
        with file_path.open(encoding="utf-8") as f:
            lines = f.readlines()

        with file_path.open("w", encoding="utf-8") as f:
            for line in lines:
                new_line, count = trailing_whitespace_pattern.subn('', line)
                if count > 0:
                    modified_lines += 1
                f.write(new_line)
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)  # noqa: T201

    return modified_lines


def main() -> int:
    """Execute the trailing whitespace checker.

    Returns:
        Exit code (0 for success, 1 for failure)

    """
    parser = argparse.ArgumentParser(
        description="Check for and remove trailing whitespace in text files"
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to search (default: current directory)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Fix trailing whitespace issues by removing them'
    )
    parser.add_argument(
        '--extensions',
        default='.py,.md,.yml,.yaml,.toml,.json,.txt,.html,.css,.js,.sh,.conf,.ini',
        help='Comma-separated list of file extensions to check (default: '
             '.py,.md,.yml,.yaml,.toml,.json,.txt,.html,.css,.js,.sh,.conf,.ini)'
    )
    parser.add_argument(
        '--exclude',
        default='.git,__pycache__,venv,.venv,dist,build,.pytest_cache,.ruff_cache',
        help='Comma-separated list of directories to exclude (default: '
             '.git,__pycache__,venv,.venv,dist,build,.pytest_cache,.ruff_cache)'
    )

    args = parser.parse_args()
    directory = Path(args.directory)
    extensions = args.extensions.split(',')
    exclude_dirs = args.exclude.split(',')

    # Convert extensions to include dot prefix if needed
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

    # Find text files
    text_files = find_text_files(directory, extensions)

    # Filter out excluded directories
    text_files = [
        f for f in text_files
        if not any(exclude_dir in str(f) for exclude_dir in exclude_dirs)
    ]

    # Check or fix files
    found_issues = False
    for file_path in text_files:
        if args.fix:
            modified_lines = remove_trailing_whitespace(file_path)
            if modified_lines > 0:
                print(f"Fixed {modified_lines} line(s) in {file_path}")  # noqa: T201
                found_issues = True
        else:
            issues = check_file_for_trailing_whitespace(file_path)
            if issues:
                print(f"Found trailing whitespace in {file_path}:")  # noqa: T201
                for line_num, line in issues:
                    # Mark trailing whitespace with '<--'
                    display_line = re.sub(r"([ \t]+)$", r"\1<--", line)
                    print(f"  Line {line_num}: {display_line}")  # noqa: T201
                found_issues = True

    if found_issues:
        if args.fix:
            print("All trailing whitespace issues fixed.")  # noqa: T201
            return 0
        else:
            print("Trailing whitespace found. Use --fix to remove it.")  # noqa: T201
            return 1
    else:
        print("No trailing whitespace found.")  # noqa: T201
        return 0


if __name__ == "__main__":
    sys.exit(main())
