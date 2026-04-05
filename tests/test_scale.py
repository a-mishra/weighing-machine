import os
import sys

sys.path.insert(0, os.getcwd())

from modules.scale import FakeHX711, ScaleMath, ScaleSensor


def main():
    math = ScaleMath()
    assert math.raw_to_kg(1100, offset=100, scale_factor=1000) == 1.0

    fake = FakeHX711([1100, 1105, 1095, 1100, 1102])
    scale = ScaleSensor(fake, offset=100, scale_factor=1000, samples=1)
    readings = [scale.read_kg() for _ in range(5)]
    assert readings[0] == 1.0
    assert scale.is_stable() is True

    tare_scale = ScaleSensor(FakeHX711([500, 500, 500]), scale_factor=100)
    tare_value = tare_scale.tare(samples=1)
    assert tare_value == 500
    print("test_scale.py OK", readings)


if __name__ == "__main__":
    main()
