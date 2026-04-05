"""Scale math and sensor wrapper logic."""

from config import (
    DEFAULT_SCALE_FACTOR,
    DEFAULT_TARE_OFFSET,
    HX711_SAMPLES,
    STABLE_TOLERANCE_KG,
    STABLE_WINDOW,
    WEIGHT_DECIMALS,
)


class ScaleMath:
    def raw_to_kg(self, raw, offset=DEFAULT_TARE_OFFSET, scale_factor=DEFAULT_SCALE_FACTOR):
        if not scale_factor:
            raise ValueError("scale_factor must not be zero")
        value = (raw - offset) / float(scale_factor)
        return round(value, WEIGHT_DECIMALS)

    def is_stable(self, values, tolerance=STABLE_TOLERANCE_KG):
        if not values:
            return False
        return max(values) - min(values) <= tolerance


class ScaleSensor:
    def __init__(
        self,
        adc,
        offset=DEFAULT_TARE_OFFSET,
        scale_factor=DEFAULT_SCALE_FACTOR,
        samples=HX711_SAMPLES,
    ):
        self.adc = adc
        self.offset = offset
        self.scale_factor = scale_factor
        self.samples = samples
        self.math = ScaleMath()
        self._history = []

    def read_raw(self):
        return self.adc.read_average(self.samples)

    def tare(self, samples=None):
        count = samples or self.samples
        self.offset = self.adc.read_average(count)
        return self.offset

    def calibrate(self, known_weight_kg, raw_value=None):
        raw_value = self.read_raw() if raw_value is None else raw_value
        if not known_weight_kg:
            raise ValueError("known_weight_kg must not be zero")
        self.scale_factor = (raw_value - self.offset) / float(known_weight_kg)
        return self.scale_factor

    def read_kg(self):
        raw = self.read_raw()
        value = self.math.raw_to_kg(raw, self.offset, self.scale_factor)
        self._history.append(value)
        if len(self._history) > STABLE_WINDOW:
            self._history.pop(0)
        return value

    def is_stable(self):
        return self.math.is_stable(self._history)


class FakeHX711:
    """Simple fake for desktop tests."""

    def __init__(self, readings=None):
        self.readings = list(readings or [1000, 1005, 995, 1000])
        self.index = 0

    def read_average(self, count):
        if not self.readings:
            return 0
        value = self.readings[self.index % len(self.readings)]
        self.index += 1
        return value
