"""
Suvyon Developer Toolkit

Tree Utilities
--------------

Public API for generating project tree reports.

This module provides a simple interface while hiding
the implementation details of TreeBuilder.

Author:
    Suvyon Development Team
"""

from __future__ import annotations

from pathlib import Path

from .tree_builder import TreeBuilder
from .tree_models import TreeOptions


def generate_tree(
    *,
    root: Path,
    output: Path,
    title: str,
    include_files: bool = True,
    show_statistics: bool = True,
    write_to_disk: bool = True,
) -> str:
    """
    Generate a filesystem tree.

    Parameters
    ----------
    root:
        Root directory to scan.

    output:
        Output text file.

    title:
        Report title.

    include_files:
        Whether files should be included.

    show_statistics:
        Whether to append statistics.

    write_to_disk:
        Whether to save the generated report.

    Returns
    -------
    str
        Generated report.
    """

    options = TreeOptions(
        root=root,
        output=output,
        title=title,
        include_files=include_files,
        show_statistics=show_statistics,
        write_to_disk=write_to_disk,
    )

    return TreeBuilder.generate(
        options,
    )


def generate_console_tree(
    *,
    root: Path,
    title: str,
) -> None:
    """
    Print a tree to the console without writing a file.
    """

    report = generate_tree(
        root=root,
        output=Path(),
        title=title,
        write_to_disk=False,
    )

    print(report)
