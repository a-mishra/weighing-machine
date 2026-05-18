"""Buzzer helper for short status tones (active buzzer: GPIO on/off)."""

import time

from config import BUZZER_FREQUENCY

try:
    from machine import Pin  # type: ignore
except ImportError:  # pragma: no cover
    Pin = None


class Buzzer:
    def __init__(
        self,
        pin,
        frequency=BUZZER_FREQUENCY,
        active_high=True,
        enabled=True,
        pin_factory=Pin,
    ):
        self.frequency = frequency
        self.active_high = active_high
        self.enabled = enabled
        self._pin = None
        if pin_factory is not None:
            self._pin = pin_factory(pin, pin_factory.OUT)
            self._set_output(False)

    def _set_output(self, on):
        if self._pin is None:
            return
        level = (1 if on else 0) if self.active_high else (0 if on else 1)
        self._pin.value(level)

    def beep(self, duration_ms=80, frequency=None):
        if not self.enabled:
            return
        self._set_output(True)
        time.sleep(duration_ms / 1000.0)
        self._set_output(False)

    def double_beep(self):
        if not self.enabled:
            return
        self.beep(60)
        time.sleep(0.08)
        self.beep(60)

    def warning_beep(self):
        if not self.enabled:
            return
        self.beep(180)
