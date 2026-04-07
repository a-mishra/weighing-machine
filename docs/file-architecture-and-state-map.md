# File Architecture and State Map

## 1) Codebase Architecture

## 1.1 Entry Point

- `main.py`  
  Initializes modules, loads persisted data, runs state machine, drives render loop.

## 1.2 Drivers

- `drivers/hx711.py`  
  Low-level ADC read support for load cell amplifier.

- `drivers/st7735.py`  
  Framebuffer-based TFT driver; handles init, drawing primitives, and buffer transfer.

## 1.3 Core Modules

- `modules/scale.py`  
  Raw-to-kg conversion, filtering, stability logic, calibration file I/O.

- `modules/encoder.py`  
  Rotary and button event capture (interrupt-based), queueing, polling expansion.

- `modules/profiles.py`  
  Profile CRUD + language + JSON persistence with normalization/validation.

- `modules/lang.py`  
  UI translation keys and localized strings.

- `modules/display_ui.py`  
  UI rendering: live screen, menu pages, calibration pages, profile list, dialogs.

- `modules/buzzer.py`  
  Audio feedback abstraction.

- `modules/cloud.py`  
  Optional upload payload/client functions.

## 1.4 Utilities / Diagnostics

- `test_lcd_colors.py`  
  Display color-path verification.

- `quick_calibration_diagnostics.py`  
  Practical on-device calibration quality inspection.

---

## 2) Data Files

- `profiles.json`  
  Active profile, language, profile list.

- `calibration.json`  
  Tare offset, scale factor (`g=1` base model), metadata.

---

## 3) Application Lifecycle

1. Build app components (`build_app()`)
2. Load calibration and profile data
3. Splash screen
4. Startup auto-tare
5. Enter continuous loop:
   - drain input events
   - state transitions
   - render on event or periodic timeout

---

## 4) State Inventory (`main.py`)

Primary states:

- `live`
- `menu`
- `profile_menu`
- `language_menu`
- `edit_name`
- `edit_g`
- `select_profile`
- `confirm_delete`
- `cal_tare`
- `cal_place`
- `cal_input`
- `cal_confirm`
- `cal_done`

---

## 5) State Transition Map (Practical)

## 5.1 Core Navigation

- `live` --click(menu action)--> `menu`
- `live` --click(profile action)--> `profile_menu`
- `live` --click(tare action)--> `live` (side effect: tare + save)

## 5.2 Menu Tree

- `menu` --back--> `live`
- `menu` --recalibration--> `cal_tare`
- `menu` --language--> `language_menu`

- `language_menu` --back--> `menu`
- `language_menu` --select language--> `live`

## 5.3 Profile Tree

- `profile_menu` --back--> `live`
- `profile_menu` --select_profile--> `select_profile`
- `profile_menu` --create_profile--> `edit_name` (create mode)
- `profile_menu` --edit_name--> `edit_name`
- `profile_menu` --edit_g--> `edit_g`
- `profile_menu` --delete_profile--> `confirm_delete`

- `select_profile` --back item/long--> `profile_menu`
- `select_profile` --profile click--> `live`

- `edit_name` --long--> `edit_g` (create mode) or `live` (edit mode)
- `edit_g` --click--> `live`

- `confirm_delete` --yes--> `live`
- `confirm_delete` --no/long--> `live`

## 5.4 Calibration Tree

- `cal_tare` --click--> `cal_place`
- `cal_place` --click--> `cal_input`
- `cal_input` --click(save point)--> `cal_confirm`
- `cal_confirm` --add another--> `cal_place`
- `cal_confirm` --finish--> `cal_done`
- `cal_done` --click/long--> `live`

Long-press in calibration intermediate states exits to `live`.

---

## 6) Event Handling Model

Events consumed by state handlers:

- `cw`
- `ccw`
- `click`
- `long`

Dispatch path:

- `encoder.poll()` -> `handle_events(events)` -> `_handle_<state>_event(event)`

This decouples input capture from state semantics.

---

## 7) Render Model

`render()` selects the draw path by state:

- live -> `draw_live(...)`
- menu-like states -> `draw_menu(...)` / `draw_profile_list(...)`
- calibration states -> calibration-specific draw methods
- edit states -> `draw_message(...)`
- delete state -> `draw_confirm_delete(...)`

Render triggers:

- immediate on user input
- periodic at `UI_REDRAW_MS`

---

## 8) Key Design Decisions

1. **Interrupt-first input**
   - prevents lag from heavy drawing loops.

2. **State-specific event handlers**
   - improves predictability and debuggability.

3. **Persistent calibration/profile storage**
   - no mandatory reconfiguration each reboot.

4. **Base mass model (`g=1`)**
   - single calibration baseline with profile gravity scaling.

---

## 9) Maintenance Guide

When adding new features:

1. Add new state key(s) in `main.py`
2. Add handler function(s) for events
3. Add rendering function(s) in `display_ui.py`
4. Add language keys in `lang.py`
5. Add persistence changes in `profiles.py`/`scale.py` if needed
6. Update test-case docs

