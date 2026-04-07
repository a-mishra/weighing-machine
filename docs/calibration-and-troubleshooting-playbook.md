# Calibration and Troubleshooting Playbook

## 1) Goal

This playbook gives a repeatable field process for:

- accurate calibration
- quick fault isolation
- stable runtime behavior

Use this during lab setup, demo preparation, and maintenance.

---

## 2) Calibration Standard Procedure (SOP)

## 2.1 Pre-Checks

Before calibration:

1. Ensure scale platform is mechanically rigid.
2. Keep no load on platform.
3. Confirm correct profile (normally Earth for baseline checks).
4. Wait for stable UI status.

## 2.2 Multi-Point Calibration Steps

1. Open `Menu` -> `Recalibration`.
2. On tare step, keep empty and click to capture tare.
3. Place known weight and click to enter value.
4. Set known value with encoder:
   - slow rotation -> 0.05 kg step
   - fast rotation -> 0.5 kg step
5. Click to save point.
6. Add at least 2-3 points across range (example: 1.0, 2.5, 5.0 kg).
7. Finish calibration and return to live screen.

Expected:
- `calibration.json` updated with new `offset` and `scale_factor`.

## 2.3 Best Practices for Better Accuracy

- Use certified/known weights.
- Spread points across expected usage range.
- Place weight at center of platform.
- Wait 1-2 seconds before confirming each point.
- Do not touch table/platform during capture.

---

## 3) Verification Procedure After Calibration

1. Test with each known weight used in calibration.
2. Test with one additional random weight.
3. Record display error:
   - absolute error = measured - reference
   - percent error = (absolute/reference) * 100
4. Repeat each point 3 times for repeatability.

Target (practical for this hardware class):
- repeatability within small band
- no constant multiplier error across all points
- monotonic increase with load

---

## 4) Troubleshooting Matrix

## 4.1 Measurement Issues

### Symptom: All readings are ~4x higher/lower
- Likely causes:
  - wrong correction factor logic
  - stale/incorrect calibration data
  - calibration performed under wrong assumptions
- Actions:
  1. inspect `WEIGHT_CORRECTION_FACTOR` (should normally be `1.0`)
  2. recalibrate with 3 points
  3. verify `calibration.json` values update

### Symptom: Readings drift while no load
- Likely causes:
  - mechanical creep
  - HX711 noise / poor ground
  - temperature effect
- Actions:
  1. recheck wiring and common ground
  2. keep cables short/twisted
  3. run manual tare
  4. validate startup auto-tare behavior

### Symptom: Very noisy unstable values
- Likely causes:
  - loose load cell mounting
  - vibration
  - electrical interference
- Actions:
  1. tighten mounting
  2. isolate from vibration
  3. confirm `HX711_SAMPLES` and stability thresholds in `config.py`

## 4.2 UI/Input Issues

### Symptom: Encoder feels laggy
- Likely causes:
  - heavy render cycle
  - event queue bursts
- Actions:
  1. confirm `UI_REDRAW_MS` tuning
  2. confirm input is interrupt-driven (`modules/encoder.py`)
  3. keep `MAIN_LOOP_DELAY_MS` reasonable

### Symptom: Selection feels like double click
- Likely causes:
  - flow-specific handler bug
  - debounce too aggressive
- Actions:
  1. test each menu with single-click checklist
  2. review `click` path in per-state handlers
  3. check `ENCODER_DEBOUNCE_MS`

## 4.3 Display/Color Issues

### Symptom: Red/Green/Blue appear swapped
- Likely causes:
  - byte order mismatch (RGB565 endian)
  - panel color order mismatch
- Actions:
  1. run `test_lcd_colors.py`
  2. verify byte-swap path in `drivers/st7735.py::show()`
  3. recheck ST7735 wiring and model variant

### Symptom: Dark looks light / inverted colors
- Likely causes:
  - panel inversion mode
- Actions:
  1. verify `INVOFF` path in display init
  2. rerun color test script

---

## 5) Quick Debug Order (Fastest Isolation)

1. `test_lcd_colors.py` for display correctness.
2. Check encoder navigation across menus.
3. Validate no-load stability.
4. Perform recalibration (3 points).
5. Verify reference weights and log errors.

---

## 6) Recovery Procedure (Known Good Reset)

If behavior is unpredictable:

1. Back up `profiles.json` if needed.
2. Remove/recreate `calibration.json`.
3. Reboot and allow startup auto-tare.
4. Recalibrate with known points.
5. Revalidate using 1.0/2.5/5.0 kg.

---

## 7) Field Log Template

Use this quick log per session:

- Date/Time:
- Build/Firmware note:
- Profile used:
- Environment notes (table stability, temperature):
- Calibration points:
- Post-calibration test weights and errors:
- Observed issues:
- Final pass/fail:

---

## 8) ASCII Quick-Action Trees

### 8.1 Calibration Decision Flow

```text
Start
 |
 +--> Empty stable? --no--> stabilize setup --> retry
 |         |
 |        yes
 |         v
 +--> Capture tare
           |
           v
     Add known point(s)
           |
           v
     >=2 good points? --no--> add more points
           |
          yes
           v
      Finish + Save
           |
           v
      Verify known weights
```

### 8.2 Symptom Triage Flow

```text
Wrong output?
 |
 +--> Color wrong? ---------> run test_lcd_colors.py -> fix display path
 |
 +--> Input lag? -----------> check IRQ input + redraw interval
 |
 +--> Scale off by factor? -> check correction factor + recalibrate
 |
 +--> Drift/noise? ---------> check wiring/mechanics + tare + filtering
```

