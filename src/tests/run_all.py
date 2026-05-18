"""Run desktop-safe unit tests under src/tests/."""

import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import path_setup  # noqa: E402, F401

_TEST_MODULES = (
    "test_lang",
    "test_scale",
    "test_profiles",
    "test_cloud",
    "test_buzzer",
    "test_display_layout",
)


def main():
    failed = []
    for name in _TEST_MODULES:
        mod = importlib.import_module(name)
        try:
            mod.main()
            print(name, "OK")
        except Exception as exc:
            failed.append((name, exc))
            print(name, "FAIL:", exc)
    if failed:
        raise SystemExit(1)
    print("All tests passed.")


if __name__ == "__main__":
    main()
