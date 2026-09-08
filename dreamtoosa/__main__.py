"""
CLI entry point when running `python3 -m dreamtoosa`.
"""

import sys
from .dreamer import main

if __name__ == "__main__":
    sys.exit(main())
