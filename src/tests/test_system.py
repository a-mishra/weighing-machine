import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import path_setup  # noqa: E402, F401

from main import build_app


def main():
    try:
        app = build_app()
    except RuntimeError as exc:
        print("test_system.py skipped on desktop:", exc)
        return
    assert app is not None
    assert hasattr(app, "send_record")
    app.render()
    print("test_system.py OK hardware app initialized")


if __name__ == "__main__":
    main()
