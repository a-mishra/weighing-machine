"""Rotary encoder wrapper using micropython-rotary library with interrupt-based button."""

import time

from config import ENCODER_DEBOUNCE_MS, ENCODER_LONG_PRESS_MS

try:
    from machine import Pin  # type: ignore
    from rotary_irq_rp2 import RotaryIRQ
    _HAS_HARDWARE = True
except ImportError:
    Pin = None
    RotaryIRQ = None
    _HAS_HARDWARE = False


def ticks_ms():
    try:
        return time.ticks_ms()
    except AttributeError:
        return int(time.time() * 1000)


def ticks_diff(newer, older):
    try:
        return time.ticks_diff(newer, older)
    except AttributeError:
        return newer - older


class EncoderState:
    def __init__(self):
        self.position = 0
        self.button_was_long = False


class RotaryEncoder:
    def __init__(self, clk_pin, dt_pin, sw_pin, pin_factory=Pin):
        self.state = EncoderState()
        self._pending_events = []
        self._last_position = 0
        
        # Button state for interrupt handler
        self._button_down_at = None
        self._last_button_irq = 0
        
        if pin_factory is None or not _HAS_HARDWARE:
            self._rotary = None
            self.sw = None
            self._mock_mode = True
        else:
            self._mock_mode = False
            self._rotary = RotaryIRQ(
                pin_num_clk=clk_pin,
                pin_num_dt=dt_pin,
                pull_up=True,
                half_step=False,
            )
            self._rotary.add_listener(self._on_rotation)
            
            # Set up interrupt-based button handling
            self.sw = pin_factory(sw_pin, pin_factory.IN, pin_factory.PULL_UP)
            self.sw.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._on_button)

    def _on_rotation(self):
        """Callback from RotaryIRQ when rotation detected."""
        new_pos = self._rotary.value()
        diff = new_pos - self._last_position
        
        if diff > 0:
            for _ in range(diff):
                self.state.position += 1
                self._pending_events.append("cw")
        elif diff < 0:
            for _ in range(-diff):
                self.state.position -= 1
                self._pending_events.append("ccw")
        
        self._last_position = new_pos

    def _on_button(self, pin):
        """Interrupt handler for button press/release."""
        now = ticks_ms()
        
        # Debounce check
        if ticks_diff(now, self._last_button_irq) < ENCODER_DEBOUNCE_MS:
            return
        self._last_button_irq = now
        
        button_state = pin.value()
        
        if button_state == 0:
            # Button pressed (falling edge)
            self._button_down_at = now
        else:
            # Button released (rising edge)
            if self._button_down_at is not None:
                held_ms = ticks_diff(now, self._button_down_at)
                if held_ms >= ENCODER_LONG_PRESS_MS:
                    self.state.button_was_long = True
                    self._pending_events.append("long")
                else:
                    self.state.button_was_long = False
                    self._pending_events.append("click")
                self._button_down_at = None

    def _read_button(self, default=1):
        if self.sw is None:
            return default
        return self.sw.value()

    def poll(self):
        """Return pending events from interrupts."""
        events = list(self._pending_events)
        self._pending_events.clear()
        return events

    def inject(self, *events):
        """Desktop test helper."""
        for event in events:
            if event == "cw":
                self.state.position += 1
            elif event == "ccw":
                self.state.position -= 1
            elif event == "long":
                self.state.button_was_long = True
            self._pending_events.append(event)
        return list(events)
