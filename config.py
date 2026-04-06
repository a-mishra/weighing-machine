"""Shared configuration for the Pico 2W weighing machine."""

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("en", "hi")

DEFAULT_G_VALUE = 9.8
MIN_G_VALUE = 1.0
MAX_G_VALUE = 50.0
G_STEP = 0.1

PROFILE_FILE = "profiles.json"
CALIBRATION_FILE = "calibration.json"

# HX711 and load-cell wiring.
HX711_DATA_PIN = 2
HX711_SCK_PIN = 3
HX711_SAMPLES = 8
HX711_GAIN = 128
DEFAULT_TARE_OFFSET = 0
DEFAULT_SCALE_FACTOR = 1000.0
WEIGHT_CORRECTION_FACTOR = 0.25  # Multiply final weight by this (0.25 = divide by 4)
WEIGHT_DECIMALS = 2
STABLE_WINDOW = 4               # Readings to keep in history (fewer = faster)
STABLE_TOLERANCE_KG = 0.10      # Green: very stable
UNSTABLE_TOLERANCE_KG = 0.20    # Yellow: somewhat stable, Red: above this
EMA_ALPHA = 0.6                 # Higher = more responsive (0-1)
STABLE_LOCK_COUNT = 3           # Consecutive stable readings before locking
STABLE_FREEZE_MS = 5000         # Freeze display for 5 seconds when locked
AUTO_TARE_TIMEOUT_MS = 5000     # Max wait for stable reading during auto-tare

# Calibration settings.
CALIBRATE_WEIGHT_STEP = 0.05       # 50 grams normal step
CALIBRATE_WEIGHT_STEP_FAST = 0.5   # 500 grams fast step
CALIBRATE_FAST_THRESHOLD_MS = 100  # Time between rotations to trigger fast mode
CALIBRATE_WEIGHT_MIN = 0.05
CALIBRATE_WEIGHT_MAX = 50.0
CALIBRATE_DEFAULT_WEIGHT = 0.5

# SPI TFT 1.8 inch 160x128 in landscape mode, ST7735-style mapping.
TFT_SPI_ID = 0
TFT_SCK_PIN = 18
TFT_MOSI_PIN = 19
TFT_CS_PIN = 17
TFT_DC_PIN = 20
TFT_RST_PIN = 21
TFT_BL_PIN = 16
TFT_WIDTH = 160
TFT_HEIGHT = 128
TFT_ROTATION = 1

# Rotary encoder.
ENCODER_CLK_PIN = 10
ENCODER_DT_PIN = 11
ENCODER_SW_PIN = 12
ENCODER_DEBOUNCE_MS = 15      # Reduced from 35 for faster response
ENCODER_LONG_PRESS_MS = 600   # Reduced from 900 for quicker long-press detection

# Buzzer.
BUZZER_PIN = 15
BUZZER_FREQUENCY = 2400

# Wi-Fi and cloud.
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
CLOUD_ENDPOINT = "http://httpbin.org/post"
CLOUD_TIMEOUT_SECONDS = 10

# UI.
SPLASH_MS = 1200
MAIN_LOOP_DELAY_MS = 30
PROFILE_NAME_LENGTH = 10
PROFILE_NAME_CHARSET = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
DEFAULT_ACTIONS = ("tare", "profile", "menu")
