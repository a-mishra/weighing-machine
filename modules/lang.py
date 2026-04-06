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
        "profiles": "Profiles",
        "back": "Back",
        "select_profile": "Select",
        "edit_name": "Edit Name",
        "edit_g": "Edit g",
        "delete_profile": "Delete",
        "recalibration": "Recalib",
        "display_calibration": "Disp Cal",
        "display_calibration_hint1": "Run test_lcd_colors",
        "display_calibration_hint2": "Click/Long: Back",
        "edit_config": "Config",
        "config_edit_hint": "Clk:Next Lng:Save",
        "reset_config": "Reset Cfg",
        "confirm_delete": "Delete?",
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
        "settling": "Settling",
        "not_ready": "Unstable",
        "locked": "Locked",
        "english": "English",
        "hindi": "Hindi",
        "calibrate": "Calibrate",
        "cal_tare": "Empty Scale",
        "cal_place": "Place Weight",
        "cal_input": "Enter Weight",
        "cal_more": "Add More?",
        "cal_done": "Calibrated!",
        "cal_raw": "Raw",
        "cal_weight_n": "Weight #",
        "yes": "Yes",
        "no": "No",
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
        "profiles": "Profiles",
        "back": "Wapas",
        "select_profile": "Chunein",
        "edit_name": "Naam Badle",
        "edit_g": "g Badle",
        "delete_profile": "Mitao",
        "recalibration": "Recalib",
        "display_calibration": "Display Cal",
        "display_calibration_hint1": "test_lcd_colors",
        "display_calibration_hint2": "Click/Long: Back",
        "edit_config": "Config",
        "config_edit_hint": "Clk:Next Lng:Save",
        "reset_config": "Reset Cfg",
        "confirm_delete": "Mitana?",
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
        "settling": "Ruk Raha",
        "not_ready": "Asthir",
        "locked": "Lock",
        "english": "Angrezi",
        "hindi": "Hindi",
        "calibrate": "Calibrate",
        "cal_tare": "Scale Khali Karo",
        "cal_place": "Vajan Rakho",
        "cal_input": "Vajan Dalo",
        "cal_more": "Aur Dalna?",
        "cal_done": "Calibrate Hua!",
        "cal_raw": "Raw",
        "cal_weight_n": "Vajan #",
        "yes": "Haan",
        "no": "Nahi",
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
