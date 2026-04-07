# Configuration Reference (`config.py`)

## 1) Language and Localization

- `DEFAULT_LANGUAGE = "en"`  
  Initial UI language.

- `SUPPORTED_LANGUAGES = ("en", "hi")`  
  Enabled language codes.

---

## 2) Gravity/Profile Settings

- `DEFAULT_G_VALUE = 9.8`  
  Fallback gravity for edits/creation.

- `MIN_G_VALUE = 1.0`  
  Lower clamp for profile gravity.

- `MAX_G_VALUE = 50.0`  
  Upper clamp for profile gravity.

- `G_STEP = 0.1`  
  Encoder increment during gravity edit.

---

## 3) Persistence Files

- `PROFILE_FILE = "profiles.json"`  
  Profile and language storage.

- `CALIBRATION_FILE = "calibration.json"`  
  Tare and scale-factor storage.

---

## 4) HX711 / Measurement Core

- `HX711_DATA_PIN = 2`  
  DOUT GPIO pin.

- `HX711_SCK_PIN = 3`  
  Clock GPIO pin.

- `HX711_SAMPLES = 12`  
  Runtime averaging count per read.
  - Higher -> smoother but slower response
  - Lower -> faster but noisier

- `HX711_GAIN = 128`  
  HX711 gain/channel mode.

- `DEFAULT_TARE_OFFSET = 0`  
  Startup fallback offset if file missing.

- `DEFAULT_SCALE_FACTOR = 1000.0`  
  Startup fallback scale factor.

- `WEIGHT_CORRECTION_FACTOR = 1.0`  
  Post-conversion multiplier for hardware correction.
  - Keep `1.0` unless validated reason.

- `WEIGHT_DECIMALS = 2`  
  Display precision.

---

## 5) Stability and Filtering

- `STABLE_WINDOW = 4`  
  Number of recent values used for stability spread.

- `STABLE_TOLERANCE_KG = 0.10`  
  Spread threshold for stable.

- `UNSTABLE_TOLERANCE_KG = 0.20`  
  Spread threshold for settling.

- `EMA_ALPHA = 0.6`  
  EMA smoothing factor.
  - Higher -> faster reaction, less smoothing
  - Lower -> smoother, slower

- `STABLE_LOCK_COUNT = 3`  
  Consecutive stable cycles required before lock.

- `STABLE_FREEZE_MS = 8000`  
  Duration of locked display state.

- `AUTO_TARE_TIMEOUT_MS = 5000`  
  Max wait for startup stability before auto-tare.

---

## 6) Calibration Wizard

- `CALIBRATE_WEIGHT_STEP = 0.05`  
  Slow-turn increment (kg).

- `CALIBRATE_WEIGHT_STEP_FAST = 0.5`  
  Fast-turn increment (kg).

- `CALIBRATE_FAST_THRESHOLD_MS = 100`  
  Rotation interval for fast-step mode.

- `CALIBRATE_RAW_AVG_COUNT = 12`  
  Raw averaging count for calibration captures.

- `CALIBRATE_WEIGHT_MIN = 0.05`  
  Minimum entered known weight.

- `CALIBRATE_WEIGHT_MAX = 100.0`  
  Maximum entered known weight.

- `CALIBRATE_DEFAULT_WEIGHT = 0.5`  
  Initial input value in calibration screen.

---

## 7) Display (ST7735)

- `TFT_SPI_ID = 0`
- `TFT_SCK_PIN = 18`
- `TFT_MOSI_PIN = 19`
- `TFT_CS_PIN = 17`
- `TFT_DC_PIN = 20`
- `TFT_RST_PIN = 21`
- `TFT_BL_PIN = 16`
- `TFT_WIDTH = 160`
- `TFT_HEIGHT = 128`
- `TFT_ROTATION = 1`

Use with current `drivers/st7735.py` implementation that performs in-place RGB565 byte swap on `show()`.

---

## 8) Encoder

- `ENCODER_CLK_PIN = 10`
- `ENCODER_DT_PIN = 11`
- `ENCODER_SW_PIN = 12`
- `ENCODER_DEBOUNCE_MS = 50`
- `ENCODER_LONG_PRESS_MS = 1500`

Tuning guidance:
- If missed clicks -> reduce debounce slightly
- If false clicks -> increase debounce slightly
- If long-press triggers too late/early -> tune long-press threshold

---

## 9) Buzzer

- `BUZZER_PIN = 15`
- `BUZZER_FREQUENCY = 2400`

Keep optional if silent operation preferred.

---

## 10) Cloud (Optional)

- `WIFI_SSID`
- `WIFI_PASSWORD`
- `CLOUD_ENDPOINT`
- `CLOUD_TIMEOUT_SECONDS`

Not critical for local weighing functionality.

---

## 11) UI Timing and Behavior

- `SPLASH_MS = 1000`  
  Splash duration.

- `MAIN_LOOP_DELAY_MS = 30`  
  Idle loop sleep.

- `UI_REDRAW_MS = 500`  
  Forced redraw interval.
  - Increase for lower CPU load
  - Decrease for smoother UI animation

- `PROFILE_NAME_LENGTH = 10`  
  Maximum editable profile length.

- `PROFILE_NAME_CHARSET = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"`  
  Allowed characters during name edit.

- `DEFAULT_ACTIONS = ("tare", "profile", "menu")`  
  Action bar order.

---

## 12) Suggested Tuning Profiles

## Faster UI Feel
- lower `HX711_SAMPLES` (e.g., 8-10)
- slightly increase `EMA_ALPHA` (e.g., 0.65-0.7)
- keep `UI_REDRAW_MS` around 300-500

## Smoother Measurement
- increase `HX711_SAMPLES` (e.g., 12-16)
- lower `EMA_ALPHA` (e.g., 0.4-0.55)
- increase stability window/tolerance carefully

Always recalibrate after major sensor/filter tuning.

---

## 13) ASCII Signal and Tuning Diagram

```text
Load Cell -> HX711 raw -> tare remove -> scale convert -> base_mass
                                                  |
                                                  v
                                            EMA/filtering
                                                  |
                                                  v
                                        multiply by profile g
                                                  |
                                                  v
                                           displayed weight
```

```text
Tuning knobs (practical effect)
----------------------------------------------
HX711_SAMPLES    : smoothness vs speed
EMA_ALPHA        : responsiveness vs damping
STABLE_WINDOW    : stability confidence vs delay
UI_REDRAW_MS     : CPU load vs UI refresh feel
STABLE_FREEZE_MS : readability vs update immediacy
----------------------------------------------
```

