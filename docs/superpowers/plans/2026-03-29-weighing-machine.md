# Weighing Machine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a modular MicroPython weighing machine for `Raspberry Pi Pico 2W` with HX711-based load-cell input, TFT display output, rotary encoder controls, buzzer feedback, bilingual UI (`English` and ASCII-safe `Hindi` transliteration), profile-based `g` storage, and manual cloud upload to a dummy HTTP endpoint.

**Architecture:** The codebase is split into low-level drivers, hardware/service modules, UI rendering, and standalone hardware test scripts. The main loop composes these modules, manages screen state, shows the live weight screen, supports profiles and language switching, and sends a selected weight record to the cloud only when the user explicitly confirms the send action.

**Tech Stack:** `MicroPython`, `machine`, `network`, `ujson/json`, `urequests` fallback support, SPI TFT (`ST7735`-style), `HX711`, GPIO rotary encoder, PWM/GPIO buzzer.

---

## File Structure

**Create:**
- `config.py`
- `main.py`
- `drivers/hx711.py`
- `drivers/st7735.py`
- `modules/__init__.py`
- `modules/buzzer.py`
- `modules/cloud.py`
- `modules/display_ui.py`
- `modules/encoder.py`
- `modules/lang.py`
- `modules/profiles.py`
- `modules/scale.py`
- `tests/test_buzzer.py`
- `tests/test_cloud.py`
- `tests/test_display.py`
- `tests/test_encoder.py`
- `tests/test_hx711.py`
- `tests/test_profiles.py`
- `tests/test_scale.py`
- `tests/test_system.py`

**Implementation notes:**
- Desktop verification should be limited to syntax and pure-Python logic paths.
- Hardware tests are intended to run on the Pico after files are copied to the board.
- The load cell arrangement is treated as one combined bridge feeding one HX711 channel.
- `Hindi` UI in v1 uses ASCII-safe transliterated labels so the default MicroPython text path can render reliably on the TFT without a custom Devanagari bitmap font.

## Task 1: Project Skeleton and Shared Configuration

**Files:**
- Create: `config.py`
- Create: `modules/__init__.py`

- [ ] **Step 1: Write the failing test**

```python
from config import DEFAULT_LANGUAGE, DEFAULT_G_VALUE, CLOUD_ENDPOINT, HX711_DATA_PIN

assert DEFAULT_LANGUAGE in ("en", "hi")
assert DEFAULT_G_VALUE == 9.8
assert CLOUD_ENDPOINT.startswith("http")
assert isinstance(HX711_DATA_PIN, int)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -c "from config import DEFAULT_LANGUAGE, DEFAULT_G_VALUE"`
Expected: import failure before implementation

- [ ] **Step 3: Write minimal implementation**

```python
DEFAULT_LANGUAGE = "en"
DEFAULT_G_VALUE = 9.8
CLOUD_ENDPOINT = "http://example.com/api/weights"
HX711_DATA_PIN = 2
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -c "from config import DEFAULT_LANGUAGE, DEFAULT_G_VALUE; print(DEFAULT_LANGUAGE, DEFAULT_G_VALUE)"`
Expected: prints `en 9.8`

## Task 2: Profile and Language Storage

**Files:**
- Create: `modules/profiles.py`
- Test: `tests/test_profiles.py`

- [ ] **Step 1: Write the failing test**

```python
from modules.profiles import ProfileStore

store = ProfileStore("profiles.json")
data = store.default_data()
assert data["active_profile"] == "default"
assert data["language"] == "en"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_profiles.py`
Expected: import failure before implementation

- [ ] **Step 3: Write minimal implementation**

```python
class ProfileStore:
    def default_data(self):
        return {"active_profile": "default", "language": "en", "profiles": [{"name": "default", "g": 9.8}]}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_profiles.py`
Expected: PASS output or successful debug prints

## Task 3: Scale Driver and Weight Conversion

**Files:**
- Create: `drivers/hx711.py`
- Create: `modules/scale.py`
- Test: `tests/test_hx711.py`
- Test: `tests/test_scale.py`

- [ ] **Step 1: Write the failing tests**

```python
from modules.scale import ScaleMath

scale = ScaleMath()
assert round(scale.raw_to_kg(1100, offset=100, scale_factor=1000), 3) == 1.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python tests/test_scale.py`
Expected: import failure before implementation

- [ ] **Step 3: Write minimal implementation**

```python
class ScaleMath:
    def raw_to_kg(self, raw, offset, scale_factor):
        return (raw - offset) / scale_factor
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python tests/test_scale.py`
Expected: conversion output validates

## Task 4: Encoder and Buzzer Modules

**Files:**
- Create: `modules/encoder.py`
- Create: `modules/buzzer.py`
- Test: `tests/test_encoder.py`
- Test: `tests/test_buzzer.py`

- [ ] **Step 1: Write the failing tests**

```python
from modules.encoder import EncoderState

state = EncoderState()
assert state.button_was_long is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python tests/test_encoder.py`
Expected: import failure before implementation

- [ ] **Step 3: Write minimal implementation**

```python
class EncoderState:
    def __init__(self):
        self.button_was_long = False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python tests/test_encoder.py`
Expected: event debug output

## Task 5: Language and Display UI

**Files:**
- Create: `modules/lang.py`
- Create: `drivers/st7735.py`
- Create: `modules/display_ui.py`
- Test: `tests/test_display.py`

- [ ] **Step 1: Write the failing tests**

```python
from modules.lang import tr

assert tr("en", "menu") == "Menu"
assert tr("hi", "menu") == "Menu Hindi"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python tests/test_display.py`
Expected: import failure before implementation

- [ ] **Step 3: Write minimal implementation**

```python
STRINGS = {"en": {"menu": "Menu"}, "hi": {"menu": "Menu Hindi"}}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python tests/test_display.py`
Expected: string and drawing debug output

## Task 6: Cloud Upload Module

**Files:**
- Create: `modules/cloud.py`
- Test: `tests/test_cloud.py`

- [ ] **Step 1: Write the failing test**

```python
from modules.cloud import build_payload

payload = build_payload("default", 9.8, 1.25, "en")
assert payload["profile_name"] == "default"
assert payload["weight_kg"] == 1.25
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_cloud.py`
Expected: import failure before implementation

- [ ] **Step 3: Write minimal implementation**

```python
def build_payload(profile_name, g_value, weight_kg, language):
    return {"profile_name": profile_name, "g_value": g_value, "weight_kg": weight_kg, "language": language}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_cloud.py`
Expected: payload debug output

## Task 7: Main Application Flow

**Files:**
- Create: `main.py`
- Test: `tests/test_system.py`

- [ ] **Step 1: Write the failing test**

```python
from main import build_app

app = build_app()
assert app is not None
assert "send_record" in dir(app)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_system.py`
Expected: import failure before implementation

- [ ] **Step 3: Write minimal implementation**

```python
class App:
    def send_record(self):
        return None

def build_app():
    return App()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_system.py`
Expected: integration smoke output

## Verification

- Run: `python -m compileall .`
- Run: `python tests/test_profiles.py`
- Run: `python tests/test_scale.py`
- Run: `python tests/test_cloud.py`
- Run: `python tests/test_system.py`
- Run on Pico: `tests/test_hx711.py`
- Run on Pico: `tests/test_display.py`
- Run on Pico: `tests/test_encoder.py`
- Run on Pico: `tests/test_buzzer.py`
- Record any hardware-dependent scripts that cannot be fully verified on this machine.
