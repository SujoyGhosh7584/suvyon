"""
Suvyon Developer Toolkit

Generate the complete Suvyon project structure.

Usage
-----
python scripts/tree_project.py
"""

from pathlib import Path

from scripts.tree_config import (
    OUTPUT_DIRECTORY,
    PROJECT_OUTPUT_FILE,
    PROJECT_ROOT,
)
from scripts.tree_utils import generate_tree


def main() -> None:
    """
    Generate the complete project tree.
    """

    generate_tree(
        root=PROJECT_ROOT,
        output=PROJECT_OUTPUT_FILE,
        title="SUVYON PROJECT STRUCTURE",
    )

    print()
    print("=" * 60)
    print("Project tree generated successfully.")
    print(f"Location : {PROJECT_OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
