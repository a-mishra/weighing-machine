"""Profile persistence for g-values and UI settings."""

try:
    import ujson as json
except ImportError:  # pragma: no cover - CPython fallback
    import json

try:
    import os
except ImportError:  # pragma: no cover
    os = None

from config import (
    DEFAULT_G_VALUE,
    DEFAULT_LANGUAGE,
    G_STEP,
    MAX_G_VALUE,
    MIN_G_VALUE,
    PROFILE_FILE,
    PROFILE_NAME_LENGTH,
)


def clamp_g_value(value):
    value = float(value)
    value = max(MIN_G_VALUE, min(MAX_G_VALUE, value))
    return round(round(value / G_STEP) * G_STEP, 1)


class ProfileStore:
    def __init__(self, path=PROFILE_FILE):
        self.path = path

    def default_data(self):
        return {
            "active_profile": "Earth",
            "language": DEFAULT_LANGUAGE,
            "profiles": [
                {"name": "Mercury", "g": 3.7},
                {"name": "Venus", "g": 8.9},
                {"name": "Earth", "g": 9.8},
                {"name": "Moon", "g": 1.6},
                {"name": "Mars", "g": 3.7},
                {"name": "Jupiter", "g": 24.8},
                {"name": "Saturn", "g": 10.4},
                {"name": "Uranus", "g": 8.9},
                {"name": "Neptune", "g": 11.2},
            ],
        }

    def _normalize(self, data):
        if not isinstance(data, dict):
            return self.default_data()

        profiles = data.get("profiles") or []
        clean = []
        seen = set()
        for item in profiles:
            name = str(item.get("name", "")).strip()[:PROFILE_NAME_LENGTH]
            if not name or name in seen:
                continue
            seen.add(name)
            clean.append({"name": name, "g": clamp_g_value(item.get("g", DEFAULT_G_VALUE))})

        if not clean:
            clean = self.default_data()["profiles"]

        active = data.get("active_profile", clean[0]["name"])
        if active not in [item["name"] for item in clean]:
            active = clean[0]["name"]

        language = data.get("language", DEFAULT_LANGUAGE)
        if language not in ("en", "hi"):
            language = DEFAULT_LANGUAGE

        return {
            "active_profile": active,
            "language": language,
            "profiles": clean,
        }

    def load(self):
        try:
            with open(self.path, "r") as handle:
                data = json.load(handle)
        except Exception:
            data = self.default_data()
            self.save(data)
        return self._normalize(data)

    def save(self, data):
        data = self._normalize(data)
        temp_path = self.path + ".tmp"
        with open(temp_path, "w") as handle:
            json.dump(data, handle)
        if os and hasattr(os, "replace"):
            os.replace(temp_path, self.path)
        elif os and hasattr(os, "rename"):
            try:
                os.remove(self.path)
            except Exception:
                pass
            os.rename(temp_path, self.path)
        else:
            with open(self.path, "w") as handle:
                json.dump(data, handle)
        return data

    def list_profiles(self):
        return self.load()["profiles"]

    def get_language(self):
        return self.load()["language"]

    def set_language(self, language):
        data = self.load()
        data["language"] = language if language in ("en", "hi") else DEFAULT_LANGUAGE
        self.save(data)
        return data["language"]

    def get_active_profile(self):
        data = self.load()
        for item in data["profiles"]:
            if item["name"] == data["active_profile"]:
                return item
        return data["profiles"][0]

    def select_profile(self, name):
        data = self.load()
        for item in data["profiles"]:
            if item["name"] == name:
                data["active_profile"] = name
                self.save(data)
                return item
        raise ValueError("Unknown profile")

    def create_profile(self, name, g_value=DEFAULT_G_VALUE):
        data = self.load()
        name = str(name).strip()[:PROFILE_NAME_LENGTH]
        if not name:
            raise ValueError("Profile name required")
        if name in [item["name"] for item in data["profiles"]]:
            raise ValueError("Profile already exists")
        profile = {"name": name, "g": clamp_g_value(g_value)}
        data["profiles"].append(profile)
        data["active_profile"] = name
        self.save(data)
        return profile

    def update_profile(self, current_name, new_name=None, g_value=None):
        data = self.load()
        names = [item["name"] for item in data["profiles"]]
        if current_name not in names:
            raise ValueError("Unknown profile")
        for item in data["profiles"]:
            if item["name"] != current_name:
                continue
            if new_name is not None:
                new_name = str(new_name).strip()[:PROFILE_NAME_LENGTH]
                if not new_name:
                    raise ValueError("Profile name required")
                if new_name != current_name and new_name in names:
                    raise ValueError("Profile already exists")
                item["name"] = new_name
                if data["active_profile"] == current_name:
                    data["active_profile"] = new_name
            if g_value is not None:
                item["g"] = clamp_g_value(g_value)
            self.save(data)
            return item
        raise ValueError("Unknown profile")
