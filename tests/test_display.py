"""Run this on the Pico to verify the TFT and UI."""

import time
import os
import sys

sys.path.insert(0, os.getcwd())

import config
from drivers.st7735 import create_default_display
from modules.display_ui import DisplayUI


def main():
    display = create_default_display(config)
    ui = DisplayUI(display)

    ui.splash("en")
    time.sleep(1)
    display.fill(display.color565(0, 0, 0))
    display.fill_rect(0, 0, display.width, 20, display.color565(0, 0, 180))
    display.fill_rect(0, 20, display.width, 20, display.color565(0, 180, 0))
    display.fill_rect(0, 40, display.width, 20, display.color565(180, 0, 0))
    display.text("128x160 Portrait", 6, 70, display.color565(255, 255, 255))
    display.show()
    time.sleep(1)
    ui.draw_live("en", 1.234, "EARTH", 9.8, True, "Ready", 0)
    time.sleep(1)
    ui.draw_live("hi", 1.876, "EARTH", 9.8, False, "Bhejna Safal", 3)
    time.sleep(1)
    ui.draw_menu("en", ["Select", "Create", "Edit Name", "Edit g", "Language", "Buzzer"], 2)
    print("Display test finished.")


if __name__ == "__main__":
    main()
