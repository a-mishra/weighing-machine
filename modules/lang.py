"""Language strings for the UI.

Hindi strings are ASCII-safe transliterations so they render on the default
MicroPython text path without a custom Devanagari font.
"""

from config import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES


STRINGS = {
    "en": {
        "title": "Weigh Machine",
        "weight": "Weight",
        "profile": "Profile",
        "gravity": "g",
        "menu": "Menu",
        "tare": "Tare",
        "send": "Send",
        "language": "Language",
        "cloud": "Cloud",
        "status": "Status",
        "create_profile": "Create",
        "select_profile": "Select",
        "edit_name": "Edit Name",
        "edit_g": "Edit g",
        "buzzer_test": "Buzzer Test",
        "wifi_connecting": "WiFi Connecting",
        "wifi_ok": "WiFi OK",
        "wifi_fail": "WiFi Fail",
        "uploading": "Uploading",
        "upload_ok": "Upload OK",
        "upload_fail": "Upload Fail",
        "saved": "Saved",
        "error": "Error",
        "stable": "Stable",
        "not_ready": "Sensor Wait",
        "english": "English",
        "hindi": "Hindi",
    },
    "hi": {
        "title": "Tolan Yantra",
        "weight": "Vajan",
        "profile": "Profile",
        "gravity": "g",
        "menu": "Menu Hindi",
        "tare": "Tare",
        "send": "Bhejein",
        "language": "Bhasha",
        "cloud": "Cloud",
        "status": "Sthiti",
        "create_profile": "Naya",
        "select_profile": "Chunein",
        "edit_name": "Naam Badle",
        "edit_g": "g Badle",
        "buzzer_test": "Buzzer Jaach",
        "wifi_connecting": "WiFi Jod Raha",
        "wifi_ok": "WiFi Juda",
        "wifi_fail": "WiFi Asafal",
        "uploading": "Bhej Raha",
        "upload_ok": "Bhejna Safal",
        "upload_fail": "Bhejna Asafal",
        "saved": "Sangrahit",
        "error": "Truti",
        "stable": "Sthir",
        "not_ready": "Sensor Taiyar Nahi",
        "english": "Angrezi",
        "hindi": "Hindi",
    },
}


def available_languages():
    return SUPPORTED_LANGUAGES


def normalize_language(language):
    if language in STRINGS:
        return language
    return DEFAULT_LANGUAGE


def tr(language, key):
    language = normalize_language(language)
    return STRINGS.get(language, {}).get(key, STRINGS[DEFAULT_LANGUAGE].get(key, key))
