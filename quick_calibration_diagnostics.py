"""Quick calibration diagnostics screen for Pico weighing machine.

Usage:
1. Upload this file and run it on Pico.
2. Rotate encoder to change known test weight.
3. Click to capture a diagnostics point.
4. Long press to tare and save offset.

This tool is intended for fast field checks after calibration.
"""

import sys
import time

sys.path.insert(0, "/lib")

import config
from drivers.hx711 import HX711
from drivers.st7735 import create_default_display
from modules.buzzer import Buzzer
from modules.encoder import RotaryEncoder
from modules.scale import ScaleSensor, load_calibration, save_calibration


KNOWN_WEIGHTS_KG = [0.5, 1.0, 2.5, 5.0, 10.0]


def ticks_ms():
    try:
        return time.ticks_ms()
    except AttributeError:
        return int(time.time() * 1000)


def ticks_diff(a, b):
    try:
        return time.ticks_diff(a, b)
    except AttributeError:
        return a - b


class QuickCalibrationDiagnostics:
    def __init__(self):
        cal_offset, cal_scale = load_calibration()
        self.scale = ScaleSensor(
            HX711(config.HX711_DATA_PIN, config.HX711_SCK_PIN, gain=config.HX711_GAIN),
            offset=cal_offset,
            scale_factor=cal_scale,
            samples=config.HX711_SAMPLES,
        )
        self.display = create_default_display(config)
        self.encoder = RotaryEncoder(config.ENCODER_CLK_PIN, config.ENCODER_DT_PIN, config.ENCODER_SW_PIN)
        self.buzzer = Buzzer(config.BUZZER_PIN)

        self.weight_idx = 1  # default 1.0 kg
        self.points = []  # (known_kg, pred_earth_kg, err_kg, raw_avg)
        self.last_redraw = 0
        self.raw_avg = 0
        self.pred_earth = 0.0
        self.err = 0.0

    def _read_raw_avg(self):
        count = max(1, int(config.CALIBRATE_RAW_AVG_COUNT))
        total = 0
        for _ in range(count):
            total += self.scale.read_raw()
        return total / float(count)

    def _compute_live(self):
        self.raw_avg = self._read_raw_avg()
        base_mass = (self.raw_avg - self.scale.offset) / float(self.scale.scale_factor or 1.0)
        self.pred_earth = base_mass * 9.8
        known = KNOWN_WEIGHTS_KG[self.weight_idx]
        self.err = self.pred_earth - known

    def _capture_point(self):
        known = KNOWN_WEIGHTS_KG[self.weight_idx]
        self.points.append((known, self.pred_earth, self.err, self.raw_avg))
        if len(self.points) > 5:
            self.points.pop(0)
        self.buzzer.beep(30)

    def _tare_and_save(self):
        self.scale.tare(samples=max(config.HX711_SAMPLES, config.CALIBRATE_RAW_AVG_COUNT))
        save_calibration(self.scale.offset, self.scale.scale_factor)
        self.points = []
        self.buzzer.double_beep()

    def _mae(self):
        if not self.points:
            return 0.0
        total = 0.0
        for _, _, err, _ in self.points:
            total += abs(err)
        return total / len(self.points)

    def _draw(self):
        d = self.display
        d.fill(0x0000)
        d.fill_rect(0, 0, d.width, 14, 0x2104)
        d.text("Quick Cal Diagnostics", 2, 3, 0xFFFF)

        known = KNOWN_WEIGHTS_KG[self.weight_idx]
        d.text("Known: %.2fkg  P:%d" % (known, len(self.points)), 2, 20, 0xFFE0)
        d.text("RawAvg: %d" % int(self.raw_avg), 2, 34, 0xFFFF)
        d.text("Offset: %d" % int(self.scale.offset), 2, 48, 0xFFFF)
        d.text("Scale : %d" % int(self.scale.scale_factor), 2, 62, 0xFFFF)

        err_color = 0x07E0 if abs(self.err) <= 0.05 else 0xFD20 if abs(self.err) <= 0.2 else 0xF81F
        d.text("PredE: %.2fkg" % self.pred_earth, 2, 76, 0x07FF)
        d.text("Err  : %+0.2fkg" % self.err, 2, 90, err_color)
        d.text("MAE  : %.2fkg" % self._mae(), 2, 104, 0xFFE0)

        d.fill_rect(0, d.height - 12, d.width, 12, 0x2104)
        d.text("Rot:Known Click:Cap Long:Tare", 1, d.height - 10, 0xFFFF)
        d.show()

    def _handle_event(self, event):
        if event == "cw":
            self.weight_idx = (self.weight_idx - 1) % len(KNOWN_WEIGHTS_KG)
        elif event == "ccw":
            self.weight_idx = (self.weight_idx + 1) % len(KNOWN_WEIGHTS_KG)
        elif event == "click":
            self._capture_point()
        elif event == "long":
            self._tare_and_save()

    def run(self):
        while True:
            events = self.encoder.poll()
            for event in events:
                self._handle_event(event)

            now = ticks_ms()
            if ticks_diff(now, self.last_redraw) >= 250 or events:
                self._compute_live()
                self._draw()
                self.last_redraw = now

            time.sleep_ms(10)


def main():
    QuickCalibrationDiagnostics().run()


if __name__ == "__main__":
    main()
