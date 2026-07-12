"""
Suvyon Developer Toolkit

Tree Configuration
------------------

Central configuration for all project tree utilities.

This module defines:

- Ignored directories
- Ignored file patterns
- Output directory
- Tree drawing characters
- Header formatting

Every tree generator imports its configuration from here,
keeping the entire toolkit consistent and easy to maintain.
"""

from pathlib import Path

# ==============================================================================
# Project Paths
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIRECTORY = PROJECT_ROOT / "docs" / "project_structure"

OUTPUT_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

# ==============================================================================
# Ignored Directories
# ==============================================================================

IGNORED_DIRECTORIES: set[str] = {
    ".git",
    ".github",
    ".venv",
    ".idea",
    ".vscode",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
    ".next",
    "build",
    "dist",
    "coverage",
    "htmlcov",
    ".turbo",
    ".cache",
    ".parcel-cache",
    ".DS_Store",
}

# ==============================================================================
# Ignored Files
# ==============================================================================

IGNORED_FILE_PATTERNS: tuple[str, ...] = (
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.log",
    "*.tmp",
    "*.swp",
    "*.swo",
    ".DS_Store",
    "Thumbs.db",
)

# ==============================================================================
# Tree Characters
# ==============================================================================

TREE_BRANCH = "├── "
TREE_LAST = "└── "
TREE_VERTICAL = "│   "
TREE_SPACE = "    "

# ==============================================================================
# Output Files
# ==============================================================================

BACKEND_OUTPUT_FILE = OUTPUT_DIRECTORY / "backend_tree.txt"

FRONTEND_OUTPUT_FILE = OUTPUT_DIRECTORY / "frontend_tree.txt"

PROJECT_OUTPUT_FILE = OUTPUT_DIRECTORY / "project_tree.txt"

# ==============================================================================
# Header
# ==============================================================================

HEADER_WIDTH = 80

HEADER_TITLE = "SUVYON PROJECT STRUCTURE"

# ==============================================================================
# Utility
# ==============================================================================


def is_directory_ignored(
    directory_name: str,
) -> bool:
    """
    Returns True if a directory should be ignored.
    """

    return directory_name in IGNORED_DIRECTORIES


def is_file_ignored(
    file_name: str,
) -> bool:
    """
    Returns True if a file matches one of the ignored patterns.
    """

    from fnmatch import fnmatch

    return any(
        fnmatch(
            file_name,
            pattern,
        )
        for pattern in IGNORED_FILE_PATTERNS
    )
