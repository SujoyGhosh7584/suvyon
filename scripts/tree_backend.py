"""
Suvyon Developer Toolkit

Generate the backend project structure.
"""

from pathlib import Path

from tree_config import (
    BACKEND_OUTPUT_FILE,
    PROJECT_ROOT,
)
from tree_utils import generate_tree


def main() -> None:
    """
    Generate the backend tree.
    """

    generate_tree(
        root=PROJECT_ROOT / "backend",
        output=BACKEND_OUTPUT_FILE,
        title="SUVYON BACKEND STRUCTURE",
    )

    print(f"Backend tree written to:\n{BACKEND_OUTPUT_FILE}")


if __name__ == "__main__":
    main()
