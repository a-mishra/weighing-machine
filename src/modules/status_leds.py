"""Red / yellow / green status LEDs (GPIO) driven by status_key and boot/lock patterns."""

import time

import config

try:
    from machine import Pin  # type: ignore
except ImportError:  # pragma: no cover
    Pin = None


_STATUS_COLORS = {
    "not_ready": "red",
    "settling": "yellow",
    "stable": "green",
    "locked": "green",
    "saved": "green",
    "upload_ok": "green",
    "error": "red",
    "upload_fail": "red",
}


class StatusLeds:
    def __init__(
        self,
        red_pin,
        yellow_pin,
        green_pin,
        active_high=True,
        pin_factory=Pin,
        buzzer=None,
    ):
        self._active_high = active_high
        self.buzzer = buzzer
        self._boot_mode = False
        self._boot_phase = 0
        self._boot_last_step_ms = 0
        self._warning_beeped = False
        self._pins = {}
        if pin_factory is not None:
            for name, pin_num in (
                ("red", red_pin),
                ("yellow", yellow_pin),
                ("green", green_pin),
            ):
                self._pins[name] = pin_factory(pin_num, pin_factory.OUT)

    def _drive(self, name, on):
        pin = self._pins.get(name)
        if pin is None:
            return
        level = (1 if on else 0) if self._active_high else (0 if on else 1)
        pin.value(level)

    def _all_off(self):
        for name in ("red", "yellow", "green"):
            self._drive(name, False)

    def show(self, color):
        """Turn on one color (red, yellow, green) or all off if color is None."""
        for name in ("red", "yellow", "green"):
            self._drive(name, name == color)

    def start_boot(self):
        self._boot_mode = True
        self._boot_phase = 0
        self._boot_last_step_ms = 0
        self._all_off()

    def boot_tick(self, now_ms):
        """R -> Y -> G chase while boot_mode is active."""
        if not self._boot_mode:
            return
        if self._boot_last_step_ms == 0:
            self._boot_last_step_ms = now_ms
            self.show("red")
            return
        try:
            elapsed = now_ms - self._boot_last_step_ms
        except TypeError:
            elapsed = int(now_ms) - int(self._boot_last_step_ms)
        if elapsed < config.LED_BOOT_CHASE_MS:
            return
        self._boot_last_step_ms = now_ms
        self._boot_phase = (self._boot_phase + 1) % 3
        self.show(("red", "yellow", "green")[self._boot_phase])

    def finish_boot(self, success=True):
        self._boot_mode = False
        if success:
            self.show("green")
            time.sleep(config.LED_BOOT_SUCCESS_MS / 1000.0)
        else:
            for _ in range(3):
                self.show("red")
                time.sleep(0.15)
                self._all_off()
                time.sleep(0.15)
        self._all_off()

    def update(self, status_key, now_ms, lock_time=None, freeze_ms=None):
        if self._boot_mode:
            return
        if (
            status_key == "locked"
            and lock_time is not None
            and freeze_ms is not None
            and config.LOCK_END_WARNING_MS > 0
        ):
            try:
                elapsed = time.ticks_diff(now_ms, lock_time)
            except AttributeError:
                elapsed = now_ms - lock_time
            remaining = freeze_ms - elapsed
            if 0 < remaining <= config.LOCK_END_WARNING_MS:
                if not self._warning_beeped and self.buzzer is not None:
                    self._warning_beeped = True
                    self.buzzer.beep(40)
                try:
                    phase = now_ms // config.LED_LOCK_WARNING_BLINK_MS
                except TypeError:
                    phase = int(now_ms) // config.LED_LOCK_WARNING_BLINK_MS
                self.show("yellow" if phase % 2 == 0 else None)
                return
        if status_key != "locked":
            self._warning_beeped = False
        self.show(_STATUS_COLORS.get(status_key))
