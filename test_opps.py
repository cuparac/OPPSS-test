"""Test runner za OPPSS Generator.

Pokreće sve testove: python test_opps.py
"""

import subprocess
import sys


def main() -> int:
    """Pokreće pytest testove.

    Returns:
        Exit code (0 = uspeh, 1 = greška)
    """
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        cwd="."
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
