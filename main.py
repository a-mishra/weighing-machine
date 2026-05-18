"""Root bootstrap: execute application entrypoint from src/main.py.

This avoids stdlib modules (like runpy) that are unavailable on MicroPython.
"""

import sys


def _prepend(path):
    if path and path not in sys.path:
        sys.path.insert(0, path)


def _setup_paths():
    # Prefer MicroPython-style absolute paths first.
    for path in ("/src/lib", "/src", "/lib", "src/lib", "src"):
        _prepend(path)


def _exec_file(path):
    with open(path, "r") as handle:
        source = handle.read()
    scope = {"__name__": "__main__", "__file__": path}
    exec(compile(source, path, "exec"), scope, scope)


def _run_src_main():
    for candidate in ("/src/main.py", "src/main.py"):
        try:
            _exec_file(candidate)
            return
        except OSError:
            continue
    raise ImportError("Unable to locate src/main.py")


if __name__ == "__main__":
    _setup_paths()
    _run_src_main()
