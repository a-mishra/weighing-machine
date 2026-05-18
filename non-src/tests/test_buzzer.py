"""Simple buzzer pattern test."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import path_setup  # noqa: E402, F401

import config
from modules.buzzer import Buzzer


def main():
    buzzer = Buzzer(config.BUZZER_PIN)
    print("Short beep")
    buzzer.beep()
    print("Double beep")
    buzzer.double_beep()
    print("Warning beep")
    buzzer.warning_beep()
    print("Buzzer test finished.")


if __name__ == "__main__":
    main()
