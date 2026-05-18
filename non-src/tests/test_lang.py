import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import path_setup  # noqa: E402, F401

from modules.lang import available_languages, tr


def main():
    assert "en" in available_languages()
    assert "hi" in available_languages()
    assert tr("en", "menu") == "Menu"
    assert tr("hi", "send") == "Bhejein"
    print("test_lang.py OK")


if __name__ == "__main__":
    main()
