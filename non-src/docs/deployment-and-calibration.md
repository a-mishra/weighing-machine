# Deployment And Calibration

## Deployment

1. Flash `MicroPython` for `Raspberry Pi Pico 2W` onto the board.

2. Connect the Pico by USB and copy the project files:
   - `main.py`
   - `config.py`
   - `drivers/`
   - `modules/`
   - `tests/`

3. Update `config.py` before first run:
   - set your real GPIO pins
   - set `WIFI_SSID`
   - set `WIFI_PASSWORD`
   - replace `CLOUD_ENDPOINT` with your real API later
   - keep a temporary `DEFAULT_SCALE_FACTOR` for now; you will calibrate it next

4. On the Pico, run module tests one by one:
   - `tests/test_hx711.py`
   - `tests/test_display.py`
   - `tests/test_encoder.py`
   - `tests/test_buzzer.py`

5. If each hardware test works, run:
   - `main.py`

If you use `mpremote`, a typical copy flow is:

```bash
mpremote connect auto fs cp -r . :
mpremote connect auto run tests/test_display.py
mpremote connect auto run tests/test_hx711.py
mpremote connect auto run main.py
```

## Wiring Check

Before calibration, verify:
- all 4 load cells are combined correctly into one bridge feeding the `HX711`
- `HX711` `DT` and `SCK` match `config.py`
- TFT `SPI`, `CS`, `DC`, `RST`, and optional backlight pin match `config.py`
- rotary `CLK`, `DT`, `SW` match `config.py`
- 5V buzzer is driven through a transistor or driver stage if current is high

## Load Cell Calibration

### Step 1: Empty-scale tare

1. Keep the platform empty.
2. Run `tests/test_hx711.py`.
3. Note that the raw readings are stable.
4. In the app, use the `Tare` action once.
5. That stores the current zero offset.

### Step 2: Use a known weight

Use a known object, for example:
- `1 kg`
- `2 kg`
- `5 kg`

The more accurate the reference, the better.

### Step 3: Read raw value with known weight

1. Place the known weight on the platform.
2. Read the average raw value from `tests/test_hx711.py`.
3. Also note the tare offset from the empty platform.

### Step 4: Calculate scale factor

Use:

```text
scale_factor = (raw_with_weight - tare_offset) / known_weight_kg
```

Example:
- tare offset = `50000`
- raw with `2 kg` = `65000`

Then:

```text
scale_factor = (65000 - 50000) / 2 = 7500
```

Put that value into `config.py` as `DEFAULT_SCALE_FACTOR`.

### Step 5: Verify

1. Restart the app.
2. Place the same known weight again.
3. Check the displayed value.
4. If slightly off, fine-tune `DEFAULT_SCALE_FACTOR`:
   - displayed too low: decrease the scale factor a little
   - displayed too high: increase the scale factor a little

## Practical Calibration Tips

- Calibrate after the full mechanical assembly is complete.
- Let the platform settle for a few seconds before reading values.
- Use the center of the platform for first calibration.
- Then test corners to confirm the 4-cell mechanical setup is balanced.
- If readings drift badly, check wiring, mounting stress, and HX711 power noise.

## Recommended First Bring-up Order

1. `tests/test_display.py`
2. `tests/test_encoder.py`
3. `tests/test_buzzer.py`
4. `tests/test_hx711.py`
5. tare empty platform
6. calibrate with known weight
7. run `main.py`
8. test profile creation, language switch, and cloud send
