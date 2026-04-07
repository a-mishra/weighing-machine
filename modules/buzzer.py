"""Buzzer helper for short status tones."""

import time

from config import BUZZER_FREQUENCY

try:
    from machine import PWM, Pin  # type: ignore
except ImportError:  # pragma: no cover
    PWM = None
    Pin = None


class Buzzer:
    def __init__(self, pin, frequency=BUZZER_FREQUENCY, pin_factory=Pin, pwm_factory=PWM):
        self.frequency = frequency
        self.enabled = False  # Buzzer disabled per runtime preference.
        if pwm_factory is not None and pin_factory is not None:
            self.pwm = pwm_factory(pin_factory(pin))
            self.pwm.duty_u16(0)
        else:
            self.pwm = None

    def beep(self, duration_ms=80, frequency=None):
        if not self.enabled:
            return
        if self.pwm is None:
            time.sleep(duration_ms / 1000.0)
            return
        self.pwm.freq(frequency or self.frequency)
        self.pwm.duty_u16(20000)
        time.sleep(duration_ms / 1000.0)
        self.pwm.duty_u16(0)

    def double_beep(self):
        if not self.enabled:
            return
        self.beep(60)
        time.sleep(0.08)
        self.beep(60)

    def warning_beep(self):
        if not self.enabled:
            return
        self.beep(180, 1800)
