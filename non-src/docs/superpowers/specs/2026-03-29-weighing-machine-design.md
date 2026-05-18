# Weighing Machine Design

## Goal
Build a modular MicroPython application for `Raspberry Pi Pico 2W` that reads weight from `4x 50 kg load cells` through an `HX711`, shows the reading on a `1.8 inch SPI TFT display`, accepts input through a `rotary encoder`, drives a `5V buzzer` for user feedback, and supports named gravity profiles where each profile stores a profile name and a configurable `g` value with a default of `9.8`.

## Scope
- Target platform: `Raspberry Pi Pico 2W`
- Runtime: `MicroPython`
- Input devices:
  - `HX711` connected to a combined 4-load-cell bridge
  - `Rotary encoder` with push switch
- Output devices:
  - `SPI TFT 128x160` display
  - `5V buzzer`
- Software goal:
  - clean modular structure
  - simple debug workflow
  - per-module hardware test scripts

## Non-Goals
- Wi-Fi connectivity
- cloud logging
- battery management
- advanced filtering or legal-for-trade certification
- multi-language UI

## High-Level Architecture
The project will be split into focused modules so each hardware concern can be tested independently. The main application will orchestrate hardware modules and UI state, while low-level drivers and device-specific logic stay isolated behind small interfaces.

Planned structure:

- `main.py`
  - boots the system
  - initializes modules
  - runs the main loop
  - handles top-level screen/menu states
- `config.py`
  - default GPIO assignments
  - display settings
  - timing constants
  - default calibration and filtering values
- `drivers/hx711.py`
  - low-level bit-banged HX711 driver
  - raw read and gain/channel control
- `drivers/st7735.py`
  - TFT low-level display driver for a common `ST7735/ST7735S` style 128x160 SPI panel
- `modules/scale.py`
  - sensor averaging
  - tare logic
  - calibration factor handling
  - conversion from raw counts to displayed mass
- `modules/display_ui.py`
  - screen drawing
  - splash/status screen
  - live weight screen
  - menu and editor rendering
- `modules/encoder.py`
  - rotary quadrature decoding
  - press detection
  - simple event queue or polling interface
- `modules/buzzer.py`
  - non-blocking or short blocking beep helpers
  - confirmation and warning patterns
- `modules/profiles.py`
  - save/load/select named gravity profiles
  - persistent storage in a JSON file
- `tests/`
  - per-module debug scripts

## Data Model
Profiles will be stored in a lightweight JSON file on the Pico filesystem.

Example shape:

```json
{
  "active_profile": "default",
  "profiles": [
    {
      "name": "default",
      "g": 9.8
    }
  ]
}
```

Rules:
- profile names should be short and user-editable through the rotary encoder
- profile names must be unique; duplicate names should be rejected during create/rename
- `g` defaults to `9.8`
- `g` is stored in `m/s^2`
- valid editable range for `g` in v1 is `1.0` to `30.0`, with `0.1` step size
- at least one profile must always exist
- the active profile is shown on the live weight screen

## User Experience
The system starts on a live screen showing:
- current measured weight
- active profile name
- active `g` value
- optional small status text for tare/calibration readiness

Encoder behavior:
- rotate on live screen: cycle a small highlighted action bar with items such as `Menu`, `Tare`, and `Profile`
- short press: select menu item / confirm edit
- long press on the live screen: open the full settings menu
- full settings menu items:
  - tare scale
  - select profile
  - create profile
  - edit profile name
  - edit `g` value
  - buzzer test

Text entry for profile name will use a rotary-driven character picker, which is simple and debuggable on embedded hardware without a keyboard.

## Weight Computation Model
The HX711 returns raw ADC counts from the combined load cell bridge. The system will:

1. Read multiple samples from the HX711
2. Average them to reduce noise
3. Subtract a stored tare offset
4. Divide by a calibration factor to obtain displayed mass in kilograms

The `g` value does not replace scale calibration in v1. In the first implementation, the main numeric reading remains the calibrated scale reading in kilograms, while the selected profile name and `g` value are persisted and shown clearly on screen. This is an explicit v1 product decision so the UI can support profile-based operating contexts without changing the base weighing algorithm.

## Hardware Assumptions
- The 4 load cells are already wired into one bridge suitable for a single HX711 module.
- The target MicroPython firmware is the board build for `Raspberry Pi Pico 2W` and the code should avoid relying on Wi-Fi-specific features.
- The TFT module is compatible with a common `ST7735` initialization sequence.
- The buzzer is controlled through a transistor or suitable driver stage if it cannot be driven directly from a GPIO.
- Reasonable default Pico GPIO assignments will be provided in `config.py` and kept easy to change.

## Default Pin Strategy
Initial code will include one sensible default mapping for:
- HX711 `DT`, `SCK`
- TFT `SPI SCK`, `MOSI`, `DC`, `RST`, `CS`, optional `BL`
- Rotary `CLK`, `DT`, `SW`
- Buzzer output

All pins will be centralized in `config.py` so hardware remapping does not require edits across modules.

## Error Handling
The system should fail visibly and debuggably:
- missing HX711 data readiness should show a sensor error state
- profile file parse failures should fall back to a default profile
- invalid `g` edits should be clamped to the v1 safe range of `1.0` to `30.0`
- display initialization failures should be easy to isolate by running the display test script

## Testing and Debugging Strategy
The codebase will include standalone module tests that can be copied to the Pico and run independently:

- `tests/test_hx711.py`
  - raw counts
  - average counts
  - ready/not-ready status
- `tests/test_scale.py`
  - tare flow
  - calibration factor sanity
  - displayed kg output
- `tests/test_display.py`
  - screen clear
  - text draw
  - color blocks
  - sample live UI render
- `tests/test_encoder.py`
  - direction detection
  - button detection
  - event printout
- `tests/test_buzzer.py`
  - short beep
  - double beep
  - warning beep
- `tests/test_profiles.py`
  - create/load/save/select profile
  - corrupted file recovery
- `tests/test_system.py`
  - integration smoke test that initializes all modules and refreshes the main screen

## Validation Criteria
The first version is successful if:
- the Pico reads stable raw values from the HX711
- the display shows the live weight value
- the active profile name and `g` value are visible on the display
- the encoder can navigate menus and edit profile data
- the buzzer confirms key actions
- each hardware block can be tested independently with a dedicated script

## Risks and Mitigations
- `TFT controller variant mismatch`
  - mitigate by isolating the display driver and keeping init values configurable
- `Encoder bounce/noise`
  - mitigate with simple debouncing and event filtering
- `HX711 noise and drift`
  - mitigate with averaging, tare support, and configurable sampling
- `UI complexity from text entry`
  - mitigate with a minimal rotary-based character entry flow
- `Filesystem corruption or missing JSON`
  - mitigate with automatic fallback to a generated default profile

## Implementation Notes
- Keep modules small and focused.
- Prefer constructor-based dependency injection where useful for testability.
- Keep blocking delays short so the UI remains responsive.
- Avoid hidden global state outside configuration and persisted profile storage.
- Use ASCII-only source and simple logging/print statements for debug scripts.
