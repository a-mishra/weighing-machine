"""Add src/ and src/lib to sys.path (import before application modules)."""

import os
import sys

_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_LIB = os.path.join(_SRC, "lib")
for _path in (_LIB, _SRC):
    if _path not in sys.path:
        sys.path.insert(0, _path)
