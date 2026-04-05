import os
import sys

sys.path.insert(0, os.getcwd())

from modules.display_ui import DisplayUI


class FakeDisplay:
    width = 128
    height = 160

    def fill(self, color):
        return None

    def text(self, text, x, y, color):
        return None

    def hline(self, x, y, w, color):
        return None

    def rect(self, x, y, w, h, color):
        return None

    def fill_rect(self, x, y, w, h, color):
        return None

    def show(self):
        return None


def main():
    ui = DisplayUI(FakeDisplay())
    layout = ui.get_action_layout()
    assert len(layout) == 4
    assert len({item["y"] for item in layout}) == 2
    assert max(item["x"] + item["w"] for item in layout) <= 128
    assert max(item["y"] + item["h"] for item in layout) <= 160
    print("test_display_layout.py OK", layout)


if __name__ == "__main__":
    main()
