"""
Suvyon Developer Toolkit

Tree Models
-----------

Data models used by the project tree utilities.

These models are intentionally separated from the tree generation
logic to follow the Single Responsibility Principle (SRP).

Author:
    Suvyon Development Team
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# ==============================================================================
# Tree Node
# ==============================================================================


@dataclass(slots=True)
class TreeNode:
    """
    Represents a file or directory in the generated tree.
    """

    name: str

    path: Path

    is_directory: bool

    children: list["TreeNode"] = field(
        default_factory=list,
    )

    def add_child(
        self,
        node: "TreeNode",
    ) -> None:
        """
        Add a child node.
        """

        self.children.append(node)

    @property
    def child_count(
        self,
    ) -> int:
        """
        Number of child nodes.
        """

        return len(self.children)


# ==============================================================================
# Tree Statistics
# ==============================================================================


@dataclass(slots=True)
class TreeStatistics:
    """
    Statistics collected while traversing the filesystem.
    """

    directories: int = 0

    files: int = 0

    ignored_directories: int = 0

    ignored_files: int = 0

    generated_lines: int = 0

    max_depth: int = 0

    def register_directory(
        self,
    ) -> None:
        """
        Increment directory count.
        """

        self.directories += 1

    def register_file(
        self,
    ) -> None:
        """
        Increment file count.
        """

        self.files += 1

    def register_ignored_directory(
        self,
    ) -> None:
        """
        Increment ignored directory count.
        """

        self.ignored_directories += 1

    def register_ignored_file(
        self,
    ) -> None:
        """
        Increment ignored file count.
        """

        self.ignored_files += 1

    def register_line(
        self,
    ) -> None:
        """
        Increment output line count.
        """

        self.generated_lines += 1

    def update_depth(
        self,
        depth: int,
    ) -> None:
        """
        Store deepest tree level reached.
        """

        if depth > self.max_depth:
            self.max_depth = depth


# ==============================================================================
# Tree Options
# ==============================================================================


@dataclass(slots=True)
class TreeOptions:
    """
    Configuration supplied to the tree generator.
    """

    root: Path

    output: Path

    title: str

    show_statistics: bool = True

    include_files: bool = True

    sort_directories_first: bool = True

    write_to_disk: bool = True
