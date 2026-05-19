import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import path_setup  # noqa: E402, F401

from modules.profiles import ProfileStore


def main():
    path = "test_profiles_runtime.json"
    store = ProfileStore(path)

    data = store.default_data()
    assert data["active_profile"] == "Earth"
    assert data["language"] == "en"

    store.save(data)
    store.create_profile("EARTH", 9.8)
    store.update_profile("EARTH", g_value=9.7)
    store.set_language("en")
    store.select_profile("EARTH")

    loaded = store.load()
    assert loaded["active_profile"] == "EARTH"
    assert loaded["language"] == "en"
    assert any(item["name"] == "EARTH" and abs(item["g"] - 9.7) < 0.001 for item in loaded["profiles"])
    print("test_profiles.py OK", loaded)

    for file_path in (path, path + ".tmp"):
        try:
            os.remove(file_path)
        except OSError:
            pass


if __name__ == "__main__":
    main()
