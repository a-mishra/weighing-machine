"""Add repository src/ and src/lib to sys.path for desktop tests."""

import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_SRC = os.path.join(_REPO_ROOT, "src")
_LIB = os.path.join(_SRC, "lib")
for _path in (_LIB, _SRC):
    if _path not in sys.path:
        sys.path.insert(0, _path)
