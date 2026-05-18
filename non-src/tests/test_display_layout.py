import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import path_setup  # noqa: E402, F401

from modules.display_ui import DisplayUI


class FakeDisplay:
    width = 128
    height = 160

    def __getattr__(self, name):
        def _noop(*args, **kwargs):
            return None

        return _noop


def main():
    ui = DisplayUI(FakeDisplay())
    ui.draw_live("en", 1.25, "Earth", 9.8, "stable", "Stable", 0)
    ui.draw_menu("en", ["Back", "Menu"], 0)
    assert ui.w == 128
    assert ui.h == 160
    print("test_display_layout.py OK")


if __name__ == "__main__":
    main()
