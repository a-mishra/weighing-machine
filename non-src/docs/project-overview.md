# Smart Weighing Machine (Pico 2W) - Project Overview

## 1) Project Summary

This project is a smart digital weighing machine built on the Raspberry Pi Pico 2W using:

- HX711 + load cell(s) for weight sensing
- ST7735 160x128 TFT for graphical display
- Rotary encoder (with push switch) for UI input
- Persistent JSON storage for profiles and calibration

The system supports normal weight measurement and gravity-profile simulation (Earth, Moon, Jupiter, custom `g`), so users can visualize how displayed weight changes with gravitational acceleration.

---

## 2) Key Capabilities

- Real-time weighing with filtering and stability detection
- Multi-point calibration with known weights
- Manual and startup auto-tare
- Profile management:
  - select profile
  - create profile
  - edit profile name
  - edit profile gravity value
  - delete profile
- Menu-driven UI with back navigation
- English/Hindi language support
- Persistent storage across reboot

---

## 3) System Architecture

### Hardware Layer
- `drivers/hx711.py`: raw ADC communication
- `drivers/st7735.py`: TFT frame buffer driver

### Core Logic Layer
- `modules/scale.py`: conversion/filtering/stability math
- `modules/encoder.py`: interrupt-driven input events
- `modules/profiles.py`: profile persistence and validation
- `modules/lang.py`: text localization

### Application Layer
- `main.py`: state machine, event routing, rendering flow, calibration flow
- `modules/display_ui.py`: all screen drawing/layout/theme logic

---

## 4) Measurement Model

The calibration is treated in a base model (`g = 1`) and displayed values are profile-scaled:

1. Read raw ADC
2. Apply tare offset
3. Convert using scale factor -> base mass
4. Displayed weight = base mass x active profile `g`

This design allows one calibration baseline while simulating different planetary gravity conditions.

---

## 5) Calibration Flow (User-Level)

1. Open recalibration
2. Keep scale empty -> capture tare
3. Place known weight
4. Enter known value with encoder
5. Optionally add more points
6. Finish and save

Calibration values are saved to `calibration.json`.

---

## 6) Persistence

### `profiles.json`
- active profile
- language
- profile list (`name`, `g`)

### `calibration.json`
- offset
- scale factor
- base model marker (`base_g`)

---

## 7) UI and UX Highlights

- Dark-themed, high-contrast UI
- Weight shown in large digits
- Stability status indicator (unstable/settling/stable/locked)
- Bottom action bar:
  - Tare
  - Profile
  - Menu
- Wrapped menu text for small TFT constraints

---

## 8) Performance/Responsiveness Strategy

- Encoder input is interrupt-driven
- Main loop prioritizes event handling before rendering
- UI redraw is throttled with periodic refresh (`UI_REDRAW_MS`)
- Buzzer logic is currently disabled to avoid blocking delays

---

## 9) Diagnostics Utilities

- `test_lcd_colors.py`: checks TFT color mapping/inversion/endian correctness
- `quick_calibration_diagnostics.py`: quick field check for calibration quality and error trend

---

## 10) Practical Caveats

- Mechanical mounting quality strongly affects noise and repeatability
- HX711 wiring and grounding quality affects drift/stability
- Full-frame TFT updates are CPU-heavy on MicroPython
- Embedded memory constraints require careful buffer strategy
- Calibration quality depends on stable known reference weights

---

## 11) Educational Value (Minor Project Relevance)

This project demonstrates end-to-end embedded engineering:

- sensor interfacing
- digital filtering
- interrupt-driven UI input
- finite state machine design
- persistent configuration/calibration storage
- performance tuning under constrained hardware

It is well-suited for a college minor project because it combines practical hardware integration with real software architecture decisions.

---

## 12) ASCII Diagrams

### 12.1 High-Level System Block Diagram

```text
                +----------------------+
                |   Rotary Encoder     |
                | (CW/CCW + Click SW)  |
                +----------+-----------+
                           |
                           v
+-----------+     +--------+---------+      +------------------+
|  Load Cell |---->|   HX711 ADC     |----->|   Scale Logic     |
+-----------+     +------------------+      |  (filter/stable)  |
                                             +---------+--------+
                                                       |
                                                       v
                                             +---------+--------+
                                             |   App State      |
                                             |   Machine        |
                                             +----+--------+----+
                                                  |        |
                                                  |        +-------------------+
                                                  v                            v
                                       +----------+---------+      +-----------+-----------+
                                       |   TFT UI Renderer  |      |  JSON Persistence     |
                                       |      ST7735        |      | profiles/calibration  |
                                       +--------------------+      +-----------------------+
```

### 12.2 Data Model (Base Mass + Profile Gravity)

```text
Raw ADC --> (raw - tare_offset) / scale_factor --> base_mass(g=1)
base_mass * profile_g --> displayed_weight
```

