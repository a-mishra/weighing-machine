"""Run this on the Pico to verify HX711 connectivity."""

import time
import os
import sys

sys.path.insert(0, os.getcwd())

import config

try:
    from drivers.hx711 import HX711
except Exception as exc:
    HX711 = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


def main():
    if HX711 is None:
        print("HX711 test import failed:", IMPORT_ERROR)
        print("Copy this project to the Pico and run again.")
        return

    try:
        sensor = HX711(config.HX711_DATA_PIN, config.HX711_SCK_PIN, gain=config.HX711_GAIN)
    except Exception as exc:
        print("HX711 hardware init failed:", exc)
        print("Check DT/SCK pin wiring and power.")
        return

    print("HX711 ready test. Press Ctrl+C to stop.")
    while True:
        try:
            print("ready=%s raw=%s avg=%s" % (sensor.is_ready(), sensor.read_raw(), sensor.read_average(3)))
            time.sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print("read error:", exc)
            time.sleep(1)


if __name__ == "__main__":
    main()
