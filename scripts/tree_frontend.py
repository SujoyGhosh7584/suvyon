"""
Suvyon Developer Toolkit

Generate the frontend project structure.
"""

from pathlib import Path

from tree_config import (
    FRONTEND_OUTPUT_FILE,
    PROJECT_ROOT,
)
from tree_utils import generate_tree


def main() -> None:
    """
    Generate the frontend tree.
    """

    frontend_directory = PROJECT_ROOT / "frontend"

    if not frontend_directory.exists():
        print("Frontend directory not found.\n" f"Expected: {frontend_directory}")
        return

    generate_tree(
        root=frontend_directory,
        output=FRONTEND_OUTPUT_FILE,
        title="SUVYON FRONTEND STRUCTURE",
    )

    print("\nFrontend tree generated successfully.")
    print(f"Output:\n{FRONTEND_OUTPUT_FILE}")


if __name__ == "__main__":
    main()
