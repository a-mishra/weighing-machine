"""Shared configuration for the Pico 2W weighing machine."""

DEFAULT_LANGUAGE = "en"  # default: "en" | initial UI language
SUPPORTED_LANGUAGES = ("en", "hi")  # default: ("en", "hi") | enabled language codes

DEFAULT_G_VALUE = 9.8  # default: 9.8 | fallback profile gravity
MIN_G_VALUE = 1.0  # default: 1.0 | minimum editable gravity
MAX_G_VALUE = 50.0  # default: 50.0 | maximum editable gravity
G_STEP = 0.1  # default: 0.1 | gravity edit increment

PROFILE_FILE = "profiles.json"  # default: "profiles.json" | profile storage file
CALIBRATION_FILE = "calibration.json"  # default: "calibration.json" | calibration storage file

# HX711 and load-cell wiring.
HX711_DATA_PIN = 2  # default: 2 | HX711 DOUT GPIO
HX711_SCK_PIN = 3  # default: 3 | HX711 SCK GPIO
HX711_SAMPLES = 12  # default: 12 | runtime raw averaging count
HX711_GAIN = 128  # default: 128 | HX711 gain/channel setting
DEFAULT_TARE_OFFSET = 0  # default: 0 | tare offset if none saved
DEFAULT_SCALE_FACTOR = 1000.0  # default: 1000.0 | scale factor if none saved
WEIGHT_CORRECTION_FACTOR = 1.0  # default: 1.0 | post-conversion correction multiplier
WEIGHT_DECIMALS = 2  # default: 2 | displayed weight decimals
STABLE_WINDOW = 4  # default: 4 | history length for stability logic
STABLE_TOLERANCE_KG = 0.10  # default: 0.10 | spread threshold for stable status
UNSTABLE_TOLERANCE_KG = 0.20  # default: 0.20 | spread threshold for settling status
EMA_ALPHA = 0.6  # default: 0.6 | EMA smoothing factor
STABLE_LOCK_COUNT = 3  # default: 3 | consecutive stable cycles before lock
STABLE_FREEZE_MS = 8000  # default: 8000 | lock hold duration in ms
AUTO_TARE_TIMEOUT_MS = 5000  # default: 5000 | startup auto-tare wait timeout

# Calibration settings.
CALIBRATE_WEIGHT_STEP = 0.05  # default: 0.05 | normal calibration weight step (kg)
CALIBRATE_WEIGHT_STEP_FAST = 0.5  # default: 0.5 | fast calibration step on quick turns (kg)
CALIBRATE_FAST_THRESHOLD_MS = 100  # default: 100 | turn interval to trigger fast step
CALIBRATE_RAW_AVG_COUNT = 12  # default: 12 | raw samples averaged per calibration read
CALIBRATE_WEIGHT_MIN = 0.05  # default: 0.05 | minimum calibration entry (kg)
CALIBRATE_WEIGHT_MAX = 100.0  # default: 100.0 | maximum calibration entry (kg)
CALIBRATE_DEFAULT_WEIGHT = 0.5  # default: 0.5 | initial calibration input (kg)

# SPI TFT 1.8 inch 160x128 in landscape mode, ST7735-style mapping.
TFT_SPI_ID = 0  # default: 0 | SPI bus id for display
TFT_SCK_PIN = 18  # default: 18 | display SCK GPIO
TFT_MOSI_PIN = 19  # default: 19 | display MOSI GPIO
TFT_CS_PIN = 17  # default: 17 | display chip-select GPIO
TFT_DC_PIN = 20  # default: 20 | display data/command GPIO
TFT_RST_PIN = 21  # default: 21 | display reset GPIO
TFT_BL_PIN = 16  # default: 16 | display backlight GPIO
TFT_WIDTH = 160  # default: 160 | display width in pixels
TFT_HEIGHT = 128  # default: 128 | display height in pixels
TFT_ROTATION = 1  # default: 1 | ST7735 rotation index

# Rotary encoder.
ENCODER_CLK_PIN = 10  # default: 10 | encoder A/CLK GPIO
ENCODER_DT_PIN = 11  # default: 11 | encoder B/DT GPIO
ENCODER_SW_PIN = 12  # default: 12 | encoder switch GPIO
ENCODER_DEBOUNCE_MS = 50  # default: 50 | button debounce time
ENCODER_LONG_PRESS_MS = 1500  # default: 1500 | long-press threshold

# Buzzer.
BUZZER_PIN = 15  # default: 15 | buzzer GPIO
BUZZER_FREQUENCY = 2400  # default: 2400 | buzzer base tone frequency

# Wi-Fi and cloud.
WIFI_SSID = "YOUR_WIFI_SSID"  # default: "YOUR_WIFI_SSID" | Wi-Fi SSID
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"  # default: "YOUR_WIFI_PASSWORD" | Wi-Fi password
CLOUD_ENDPOINT = "http://httpbin.org/post"  # default: "http://httpbin.org/post" | upload endpoint
CLOUD_TIMEOUT_SECONDS = 10  # default: 10 | cloud request timeout

# UI.
SPLASH_MS = 1000  # default: 1000 | splash screen duration
MAIN_LOOP_DELAY_MS = 30  # default: 30 | base loop sleep when idle
UI_REDRAW_MS = 500  # default: 500 | periodic redraw interval
PROFILE_NAME_LENGTH = 10  # default: 10 | max profile name length
PROFILE_NAME_CHARSET = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"  # default: " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" | editable profile chars
DEFAULT_ACTIONS = ("tare", "profile", "menu")  # default: ("tare", "profile", "menu") | bottom action bar order
