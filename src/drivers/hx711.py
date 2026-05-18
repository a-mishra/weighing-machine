"""Minimal HX711 driver for MicroPython."""

try:
    from machine import Pin  # type: ignore
except ImportError:  # pragma: no cover
    Pin = None

try:
    from utime import sleep_us  # type: ignore
except ImportError:  # pragma: no cover
    from time import sleep as _sleep

    def sleep_us(value):
        _sleep(value / 1000000.0)


class HX711:
    GAIN_PULSES = {128: 1, 64: 3, 32: 2}

    def __init__(self, data_pin, clock_pin, gain=128, pin_factory=Pin):
        if pin_factory is None:
            raise RuntimeError("machine.Pin is required on hardware")
        self.data = data_pin if hasattr(data_pin, "value") else pin_factory(data_pin, pin_factory.IN)
        self.clock = clock_pin if hasattr(clock_pin, "value") else pin_factory(clock_pin, pin_factory.OUT)
        self.clock.value(0)
        self.set_gain(gain)

    def set_gain(self, gain):
        if gain not in self.GAIN_PULSES:
            raise ValueError("Unsupported HX711 gain")
        self.gain = gain
        self._gain_pulses = self.GAIN_PULSES[gain]

    def is_ready(self):
        return self.data.value() == 0

    def read_raw(self, timeout_ms=1000):
        wait_loops = timeout_ms * 10
        while not self.is_ready():
            sleep_us(100)
            wait_loops -= 1
            if wait_loops <= 0:
                raise TimeoutError("HX711 not ready")

        value = 0
        for _ in range(24):
            self.clock.value(1)
            sleep_us(1)
            value = (value << 1) | self.data.value()
            self.clock.value(0)
            sleep_us(1)

        for _ in range(self._gain_pulses):
            self.clock.value(1)
            sleep_us(1)
            self.clock.value(0)
            sleep_us(1)

        if value & 0x800000:
            value -= 0x1000000
        return value

    def read_average(self, count=8):
        total = 0
        for _ in range(count):
            total += self.read_raw()
        return total / float(count)
