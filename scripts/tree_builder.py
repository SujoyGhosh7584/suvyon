"""
Suvyon Developer Toolkit

Tree Builder
------------

Core filesystem traversal engine responsible for building
beautiful project tree representations.

Responsibilities
----------------
- Walk directories recursively
- Apply ignore rules
- Build tree nodes
- Collect statistics
- Render Linux-style tree
- Generate report header
- Write output

Author:
    Suvyon Development Team
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from tree_config import (
    HEADER_TITLE,
    HEADER_WIDTH,
    IGNORED_DIRECTORIES,
    TREE_BRANCH,
    TREE_LAST,
    TREE_SPACE,
    TREE_VERTICAL,
    is_directory_ignored,
    is_file_ignored,
)
from tree_models import (
    TreeNode,
    TreeOptions,
    TreeStatistics,
)


class TreeBuilder:
    """
    Builds a filesystem tree.

    One instance is used for one generated tree.
    """

    def __init__(
        self,
        options: TreeOptions,
    ) -> None:

        self.options = options

        self.statistics = TreeStatistics()

    # ==========================================================
    # Public API
    # ==========================================================

    def build(
        self,
    ) -> str:
        """
        Build the entire report.

        Returns
        -------
        str
            Complete formatted report.
        """

        root = self._scan_directory(
            self.options.root,
            depth=0,
        )

        lines: list[str] = []

        lines.extend(
            self._build_header(),
        )

        self._render_tree(
            node=root,
            prefix="",
            is_last=True,
            lines=lines,
        )

        if self.options.show_statistics:

            lines.extend(
                self._build_statistics(),
            )

        report = "\n".join(lines)

        if self.options.write_to_disk:

            self.options.output.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            self.options.output.write_text(
                report,
                encoding="utf-8",
            )

        return report

    # ==========================================================
    # Filesystem Scanning
    # ==========================================================

    def _scan_directory(
        self,
        directory: Path,
        depth: int,
    ) -> TreeNode:
        """
        Scan a directory recursively.
        """

        self.statistics.register_directory()

        self.statistics.update_depth(
            depth,
        )

        node = TreeNode(
            name=directory.name,
            path=directory,
            is_directory=True,
        )

        try:

            entries = sorted(
                directory.iterdir(),
                key=lambda item: (
                    item.is_file(),
                    item.name.lower(),
                ),
            )

        except PermissionError:

            return node

        for entry in entries:

            if entry.is_dir():

                if is_directory_ignored(
                    entry.name,
                ):

                    self.statistics.register_ignored_directory()

                    continue

                child = self._scan_directory(
                    entry,
                    depth + 1,
                )

                node.add_child(
                    child,
                )

            else:

                if is_file_ignored(
                    entry.name,
                ):

                    self.statistics.register_ignored_file()

                    continue

                self.statistics.register_file()

                node.add_child(
                    TreeNode(
                        name=entry.name,
                        path=entry,
                        is_directory=False,
                    )
                )

        return node

    # ==========================================================
    # Rendering
    # ==========================================================

    def _render_tree(
        self,
        node: TreeNode,
        prefix: str,
        is_last: bool,
        lines: list[str],
    ) -> None:
        """
        Render one node recursively.
        """

        connector = TREE_LAST if is_last else TREE_BRANCH

        if prefix == "":

            lines.append(
                node.name,
            )

        else:

            lines.append(f"{prefix}{connector}{node.name}")

        self.statistics.register_line()

        next_prefix = prefix + (TREE_SPACE if is_last else TREE_VERTICAL)

        total = len(
            node.children,
        )

        for index, child in enumerate(
            node.children,
        ):

            self._render_tree(
                node=child,
                prefix=next_prefix,
                is_last=index == total - 1,
                lines=lines,
            )

    # ==========================================================
    # Report Header
    # ==========================================================

    def _build_header(
        self,
    ) -> list[str]:
        """
        Build the report header.
        """

        separator = "=" * HEADER_WIDTH

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S",
        )

        return [
            separator,
            HEADER_TITLE.center(
                HEADER_WIDTH,
            ),
            separator,
            "",
            f"Generated : {timestamp}",
            f"Root      : {self.options.root.resolve()}",
            "",
        ]

    # ==========================================================
    # Statistics
    # ==========================================================

    def _build_statistics(
        self,
    ) -> list[str]:
        """
        Build the statistics section.
        """

        separator = "=" * HEADER_WIDTH

        return [
            "",
            separator,
            "Statistics",
            separator,
            "",
            f"Directories         : {self.statistics.directories}",
            f"Files               : {self.statistics.files}",
            "",
            f"Ignored Directories : {self.statistics.ignored_directories}",
            f"Ignored Files       : {self.statistics.ignored_files}",
            "",
            f"Maximum Depth       : {self.statistics.max_depth}",
            f"Generated Lines     : {self.statistics.generated_lines}",
            "",
        ]

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _is_hidden(
        path: Path,
    ) -> bool:
        """
        Return True if the path is hidden.
        """

        return path.name.startswith(
            ".",
        )

    @staticmethod
    def _safe_name(
        path: Path,
    ) -> str:
        """
        Safely return the display name for a path.
        """

        try:
            return path.name

        except Exception:
            return str(
                path,
            )

    @staticmethod
    def _sorted_entries(
        directory: Path,
    ) -> list[Path]:
        """
        Return entries sorted with directories first,
        then alphabetically.
        """

        return sorted(
            directory.iterdir(),
            key=lambda item: (
                item.is_file(),
                item.name.lower(),
            ),
        )

    # ==========================================================
    # Validation
    # ==========================================================

    def _validate_root(
        self,
    ) -> None:
        """
        Validate the configured root directory.
        """

        if not self.options.root.exists():

            raise FileNotFoundError(f"Directory not found: {self.options.root}")

        if not self.options.root.is_dir():

            raise NotADirectoryError(
                str(
                    self.options.root,
                )
            )

    # ==========================================================
    # Public Utility
    # ==========================================================

    @classmethod
    def generate(
        cls,
        options: TreeOptions,
    ) -> str:
        """
        Convenience method used by the wrapper scripts.

        Example
        -------
        TreeBuilder.generate(options)
        """

        builder = cls(
            options,
        )

        builder._validate_root()

        return builder.build()

    # ==========================================================
    # Public Properties
    # ==========================================================

    @property
    def total_directories(
        self,
    ) -> int:
        """
        Total discovered directories.
        """

        return self.statistics.directories

    @property
    def total_files(
        self,
    ) -> int:
        """
        Total discovered files.
        """

        return self.statistics.files

    @property
    def ignored_directories(
        self,
    ) -> int:
        """
        Total ignored directories.
        """

        return self.statistics.ignored_directories

    @property
    def ignored_files(
        self,
    ) -> int:
        """
        Total ignored files.
        """

        return self.statistics.ignored_files

    # ==========================================================
    # Report Helpers
    # ==========================================================

    def summary(
        self,
    ) -> dict[str, int]:
        """
        Return statistics as a dictionary.
        """

        return {
            "directories": self.statistics.directories,
            "files": self.statistics.files,
            "ignored_directories": self.statistics.ignored_directories,
            "ignored_files": self.statistics.ignored_files,
            "generated_lines": self.statistics.generated_lines,
            "maximum_depth": self.statistics.max_depth,
        }

    # ==========================================================
    # Future Extension Hooks
    # ==========================================================

    def before_scan(
        self,
    ) -> None:
        """
        Hook executed before scanning starts.

        Intended for future extensions.
        """

        return None

    def after_scan(
        self,
    ) -> None:
        """
        Hook executed after scanning completes.

        Intended for future extensions.
        """

        return None

    def before_render(
        self,
    ) -> None:
        """
        Hook executed before rendering.

        Intended for future extensions.
        """

        return None

    def after_render(
        self,
    ) -> None:
        """
        Hook executed after rendering.

        Intended for future extensions.
        """

        return None

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"root={self.options.root!s}, "
            f"directories={self.statistics.directories}, "
            f"files={self.statistics.files})"
        )
