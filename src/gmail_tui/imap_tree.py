"""IMAP directory tree module.

SPDX-FileCopyrightText: 2024 Chen Linxuan <me@black-desk.cn>
SPDX-License-Identifier: GPL-3.0-or-later
"""

from collections import defaultdict


class IMAPTree:
    """IMAP directory tree class."""

    def __init__(self, folders: list[tuple[list[bytes], bytes, bytes]]) -> None:
        """Initialize IMAP directory tree.

        Args:
            folders: List of IMAP folder tuples (flags, delimiter, name)

        """
        if not folders:
            raise ValueError("No folders provided")

        self.delimiter = self._decode_flag(folders[0][1])
        self.tree = self._build_tree(folders)

    @staticmethod
    def _decode_flag(flag: bytes | str) -> str:
        """Decode IMAP flag.

        Args:
            flag: IMAP flag (bytes or str)

        Returns:
            Decoded flag string

        """
        if isinstance(flag, bytes):
            return flag.decode()
        return str(flag)

    def _build_tree(
        self, folders: list[tuple[list[bytes], bytes, bytes]]
    ) -> dict[str, set[str]]:
        """Build a tree structure from folder list.

        Args:
            folders: List of IMAP folder tuples (flags, delimiter, name)

        Returns:
            Dictionary representing the folder tree

        """
        tree: dict[str, set[str]] = defaultdict(set)
        root_folders = set()

        for _, _, name in folders:
            name = self._decode_flag(name)
            parts = name.split(self.delimiter)

            if len(parts) == 1:
                root_folders.add(name)
            else:
                parent = self.delimiter.join(parts[:-1])
                tree[parent].add(name)

        tree[""] = root_folders
        return tree

    def print_tree(self) -> None:
        """Print folder tree in tree-like format."""
        self._print_node()

    def _print_node(self, root: str = "", prefix: str = "") -> None:
        """Print a node and its children in tree-like format.

        Args:
            root: Current root folder
            prefix: Prefix for current line

        """
        folders = sorted(self.tree[root])
        for i, folder in enumerate(folders):
            is_last = i == len(folders) - 1
            if root == "":
                current = folder
            else:
                current = folder.split(self.delimiter)[-1]

            print(f"{prefix}{'└── ' if is_last else '├── '}{current}")

            if folder in self.tree:
                self._print_node(folder, prefix + ("    " if is_last else "│   "))
