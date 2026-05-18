# Smart Weighing Machine - Technical Deep Dive

## 1) Scope

This document covers implementation-level details of the Pico 2W weighing machine project:

- execution model
- state machine design
- input event pipeline
- calibration math
- filtering/stability logic
- rendering/performance trade-offs
- persistence and failure cases

It is intended for maintainers and evaluators who want practical code-level understanding.

---

## 2) Runtime Execution Model

Main loop (`main.py`) follows:

1. Drain interrupt event queue (encoder/button) first
2. Handle events through state-specific handlers
3. Render only on:
   - fresh user input, or
   - periodic timeout (`UI_REDRAW_MS`)
4. Sleep briefly only when no pending events

This gives input priority and limits unnecessary frame pushes.

---

## 3) State Machine Design

Core states currently include:

- `live`
- `menu`
- `profile_menu`
- `language_menu`
- `select_profile`
- `edit_name`
- `edit_g`
- `confirm_delete`
- calibration states:
  - `cal_tare`
  - `cal_place`
  - `cal_input`
  - `cal_confirm`
  - `cal_done`

Event dispatch pattern:

- `handle_events(events)` routes each event to state-specific function
- every state owns its `cw/ccw/click/long` behavior

This keeps logic explicit and lowers accidental cross-state side effects.

---

## 4) Input Subsystem (Interrupt-Safe)

File: `modules/encoder.py`

### Current strategy
- Rotation source: `RotaryIRQ` callback (`_on_rotation`)
- Button source: GPIO IRQ on rising/falling (`_on_button`)
- No string allocations in ISR

### Internal buffering
- Fixed-size event ring (`bytearray`) for button events (compact integer codes)
- Rotation accumulated as signed delta (`_pending_delta`) in ISR
- Expansion to `"cw"`/`"ccw"` strings happens in `poll()` (non-ISR context)

### Why this matters
MicroPython ISR context is sensitive to heap allocations. This design avoids:
- list growth in ISR
- string appends in ISR
- per-step heavy work in interrupt context

Practical effect: fewer missed events under fast encoder movement.

---

## 5) Sensor Reading + Filtering Pipeline

File: `modules/scale.py`

### Raw acquisition
- `read_raw()` -> `HX711.read_average(HX711_SAMPLES)`
- runtime sample count is configurable via `HX711_SAMPLES`

### Calibration averaging API
- `read_raw_avg(count)` was added to centralize averaging logic at scale layer
- prevents accidental nested averaging in consumers

### Conversion
- `raw_to_kg()`:
  - `(raw - offset) / scale_factor`
  - multiplied by `WEIGHT_CORRECTION_FACTOR`
  - rounded to `WEIGHT_DECIMALS`

### Runtime smoothing
- EMA update in `read_kg()`
- `read_filtered_kg()` uses EMA result (lighter CPU path)

### Stability classification
- Based on spread over recent window (`STABLE_WINDOW`)
- thresholds:
  - `<= STABLE_TOLERANCE_KG` -> stable
  - `<= UNSTABLE_TOLERANCE_KG` -> settling
  - else unstable

---

## 6) Weight Lock Logic

Implemented in `main.py::refresh_weight()`.

1. If stable, increment consecutive count
2. When count reaches `runtime_stable_lock_count`, capture `locked_weight` and `lock_time`
3. Show locked value for `runtime_stable_freeze_ms`
4. Unlock automatically after timeout

Important:
- lock does not block user input
- it only freezes displayed weight temporarily

---

## 7) Calibration Math

### Multi-point capture
Each calibration point stores:
- averaged raw reading
- entered known weight

### Gravity-aware conversion
Entered weight is converted to base model (`g=1`) using active profile gravity:

- `base_mass = entered_weight / profile_g`

### Scale factor estimation
Current fit uses fixed-offset least-squares slope:

- `raw - tare = scale_factor * base_mass`
- `scale_factor = sum(base_mass * raw_delta) / sum(base_mass^2)`

This is more robust than naive averaging of per-point factors.

---

## 8) Persistence and Data Contracts

### `profiles.json`
- `active_profile`
- `language`
- list of `{name, g}`

### `calibration.json`
- `offset`
- `scale_factor`
- `base_g` metadata

### Save points
- manual tare saves
- startup auto-tare saves
- calibration completion saves
- profile operations save through `ProfileStore`

---

## 9) Display Driver and Color Handling

File: `drivers/st7735.py`

The project uses full-frame RGB565 buffer with ST7735 SPI push.

### Endianness handling
Driver swaps bytes in-place before write and swaps back after write:
- required because framebuffer byte order and panel bus expectation differ

### Performance caveat
This full-frame swap + full-frame write is CPU-intensive on Pico.
Redraw throttling (`UI_REDRAW_MS`) is used to reduce load.

---

## 10) UI Rendering Caveats

File: `modules/display_ui.py`

- UI is currently mostly full-screen redraw per render call.
- Menu text wrapping supports:
  - word wrap first
  - character split fallback for long words
- Action bar uses custom width distribution to keep labels readable.

Potential future optimization:
- static background caching per state
- dirty-rect redraw for dynamic fields only

---

## 11) Practical Failure Modes and Mitigations

1. **Noisy analog readings**
   - mitigated via averaging + EMA + stability window

2. **ISR instability under burst input**
   - mitigated by allocation-safe event buffering

3. **Slow UI feel**
   - mitigated by redraw throttling and input-first loop

4. **Memory pressure**
   - display swap done in-place (no duplicate framebuffer allocation)

5. **Calibration mismatch**
   - mitigated by multi-point slope fit and diagnostics script

---

## 12) Practical Test Checklist

### Functional
- Encoder rotate/click/long in each menu state
- Profile create/edit/delete/select cycle
- Language selection persistence
- Calibration flow with 1, 2.5, 5 kg

### Measurement
- Earth profile accuracy at reference weights
- Repeatability (multiple placements of same weight)
- Drift after 5-10 minutes

### Performance
- Input latency in live screen and menus
- Responsiveness under rapid encoder turns

### Display
- Color correctness via `test_lcd_colors.py`
- menu wrapping correctness for long labels

---

## 13) Recommended Next Technical Improvements

1. Move display to partial redraw (dirty regions)
2. Add non-blocking optional buzzer scheduler (if buzzer re-enabled)
3. Persist editable runtime config (`settings.json`)
4. Add diagnostics counters:
   - dropped ISR events
   - render time
   - loop jitter
5. Add automated unit tests for:
   - state transitions
   - calibration fit math
   - profile persistence behavior

---

## 14) Conclusion

The project is already a strong embedded system implementation with clear modular boundaries and practical fixes for real-world constraints (noise, UI lag, ISR safety, memory limits).

Its architecture is suitable for academic demonstration and can be further productized with incremental performance and testability improvements.

---

## 15) ASCII Diagrams

### 15.1 Runtime Loop Priority

```text
while True:
   poll encoder IRQ queue
      |
      +--> if events: handle_events()
      |
   check render timer
      |
      +--> render if (had_events OR redraw_timeout)
      |
   sleep only if no pending input
```

### 15.2 ISR-Safe Input Pipeline

```text
GPIO IRQ / Rotary callback
          |
          v
  +-----------------------+
  | compact event storage |
  | ring + pending delta  |
  +-----------+-----------+
              |
              v
         poll() in main loop
              |
              v
    expanded events: cw/ccw/click/long
              |
              v
        state-specific handlers
```

### 15.3 Calibration Fit Path

```text
Empty scale  --> capture tare_offset
Known loads  --> capture (raw_i, weight_i)
                 |
                 v
         convert weight_i to base_mass_i
                 |
                 v
 scale_factor = sum(base_mass_i * (raw_i - tare)) / sum(base_mass_i^2)
                 |
                 v
 save offset + scale_factor --> calibration.json
```

