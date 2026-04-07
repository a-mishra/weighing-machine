# Hardware Wiring and Pinout

## 1) Hardware Used

- Raspberry Pi Pico 2W
- HX711 amplifier + load cell module
- ST7735 TFT display (160x128, SPI)
- Rotary encoder with push switch
- Optional buzzer module

---

## 2) Pin Mapping (From Current `config.py`)

## 2.1 HX711

- `HX711_DATA_PIN` -> GPIO `2` (HX711 `DOUT`)
- `HX711_SCK_PIN` -> GPIO `3` (HX711 `SCK`)
- `HX711_GAIN` -> `128` (software setting)

Power:
- HX711 `VCC` -> 3.3V (preferred)
- HX711 `GND` -> GND

## 2.2 ST7735 TFT (SPI0)

- `TFT_SCK_PIN` -> GPIO `18` (`SCL/SCK`)
- `TFT_MOSI_PIN` -> GPIO `19` (`SDA/MOSI`)
- `TFT_CS_PIN` -> GPIO `17` (`CS`)
- `TFT_DC_PIN` -> GPIO `20` (`DC/A0`)
- `TFT_RST_PIN` -> GPIO `21` (`RST/RES`)
- `TFT_BL_PIN` -> GPIO `16` (`BL/LED`)

Software:
- `TFT_SPI_ID = 0`
- `TFT_WIDTH = 160`
- `TFT_HEIGHT = 128`
- `TFT_ROTATION = 1`

## 2.3 Rotary Encoder

- `ENCODER_CLK_PIN` -> GPIO `10` (`CLK/A`)
- `ENCODER_DT_PIN` -> GPIO `11` (`DT/B`)
- `ENCODER_SW_PIN` -> GPIO `12` (`SW`)

Electrical:
- Input uses pull-up; switch press reads low (0).

## 2.4 Optional Buzzer

- `BUZZER_PIN` -> GPIO `15`

If using an active buzzer module:
- `VCC` -> 3.3V or 5V as module allows
- `GND` -> GND
- `SIG` -> GPIO15

If using bare passive buzzer:
- use transistor driver if current draw is uncertain.

---

## 3) Recommended Wiring Table

| Device | Device Pin | Pico Pin |
|---|---|---|
| HX711 | VCC | 3.3V |
| HX711 | GND | GND |
| HX711 | DOUT | GPIO2 |
| HX711 | SCK | GPIO3 |
| ST7735 | VCC | 3.3V |
| ST7735 | GND | GND |
| ST7735 | SCL/SCK | GPIO18 |
| ST7735 | SDA/MOSI | GPIO19 |
| ST7735 | CS | GPIO17 |
| ST7735 | DC/A0 | GPIO20 |
| ST7735 | RST | GPIO21 |
| ST7735 | BL/LED | GPIO16 |
| Encoder | CLK | GPIO10 |
| Encoder | DT | GPIO11 |
| Encoder | SW | GPIO12 |
| Encoder | + | 3.3V |
| Encoder | GND | GND |
| Buzzer (optional) | SIG | GPIO15 |
| Buzzer (optional) | VCC | 3.3V |
| Buzzer (optional) | GND | GND |

---

## 4) Load Cell to HX711 Connection

Typical 4-wire color mapping (verify your sensor datasheet):

- Red -> `E+`
- Black -> `E-`
- White -> `A-`
- Green -> `A+`

If readings move negative/inverted under load:
- swap `A+` and `A-`.

---

## 5) Power and Safety Notes

- Prefer common ground between all modules.
- Keep HX711 and load-cell wires short or twisted to reduce noise.
- Avoid powering high-current accessories from Pico GPIO.
- For unknown buzzer current, use transistor + resistor + diode-safe topology.

---

## 6) Common Wiring Faults and Symptoms

- **Wrong HX711 pins** -> random/noisy or constant reading.
- **Display MOSI/SCK swapped** -> blank/garbled TFT.
- **Missing DC/CS/RST** -> display initializes inconsistently.
- **No common GND** -> unstable ADC, random UI behavior.
- **Encoder SW floating** -> false clicks/long-press events.

---

## 7) Bring-Up Checklist

1. Power only Pico + TFT first, confirm splash.
2. Add encoder, verify menu navigation.
3. Add HX711 and confirm raw changes with load.
4. Run `test_lcd_colors.py` to confirm color channel mapping.
5. Run calibration flow before final measurements.

---

## 8) ASCII Wiring Diagram (Quick View)

```text
                      Raspberry Pi Pico 2W
               +----------------------------------+
               | GP2  <----- HX711 DOUT           |
               | GP3  -----> HX711 SCK            |
               |                                  |
               | GP18 -----> TFT SCK              |
               | GP19 -----> TFT MOSI             |
               | GP17 -----> TFT CS               |
               | GP20 -----> TFT DC               |
               | GP21 -----> TFT RST              |
               | GP16 -----> TFT BL               |
               |                                  |
               | GP10 <-----> ENC CLK             |
               | GP11 <-----> ENC DT              |
               | GP12 <-----  ENC SW              |
               |                                  |
               | GP15 ----->  BUZZER SIG (opt)    |
               |                                  |
               | 3V3  -----> HX711/TFT/ENC VCC    |
               | GND  -----  Common Ground        |
               +----------------------------------+
```

### 8.1 Load Cell to HX711 (Typical)

```text
Load Cell             HX711
---------             -----
Red   --------------> E+
Black --------------> E-
Green --------------> A+
White --------------> A-
```

