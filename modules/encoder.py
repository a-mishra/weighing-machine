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
    _EVT_CLICK = 1
    _EVT_LONG = 2

    def __init__(self, clk_pin, dt_pin, sw_pin, pin_factory=Pin):
        self.state = EncoderState()
        # Fixed-size IRQ-safe event ring (button events only).
        self._event_ring = bytearray(32)
        self._event_head = 0
        self._event_tail = 0
        self._dropped_events = 0
        # Rotation accumulated in IRQ, expanded in poll().
        self._pending_delta = 0
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

    def _queue_event_code(self, event_code):
        """Queue a compact event code without heap allocation."""
        next_head = (self._event_head + 1) % len(self._event_ring)
        if next_head == self._event_tail:
            self._dropped_events += 1
            return
        self._event_ring[self._event_head] = event_code
        self._event_head = next_head

    def _on_rotation(self):
        """Callback from RotaryIRQ when rotation detected."""
        new_pos = self._rotary.value()
        diff = new_pos - self._last_position
        if diff:
            # Keep ISR constant-time; expand to cw/ccw events in poll().
            self._pending_delta += diff
            # Clamp to avoid runaway accumulation.
            if self._pending_delta > 127:
                self._pending_delta = 127
            elif self._pending_delta < -127:
                self._pending_delta = -127
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
                    self._queue_event_code(self._EVT_LONG)
                else:
                    self.state.button_was_long = False
                    self._queue_event_code(self._EVT_CLICK)
                self._button_down_at = None

    def _read_button(self, default=1):
        if self.sw is None:
            return default
        return self.sw.value()

    def poll(self):
        """Return pending events from interrupts."""
        events = []

        # Expand queued rotation steps outside IRQ context.
        delta = self._pending_delta
        if delta:
            if delta > 0:
                for _ in range(delta):
                    self.state.position += 1
                    events.append("cw")
            else:
                for _ in range(-delta):
                    self.state.position -= 1
                    events.append("ccw")
            self._pending_delta = 0

        # Drain compact button events.
        while self._event_tail != self._event_head:
            code = self._event_ring[self._event_tail]
            self._event_tail = (self._event_tail + 1) % len(self._event_ring)
            if code == self._EVT_CLICK:
                events.append("click")
            elif code == self._EVT_LONG:
                events.append("long")
        return events

    def has_pending_events(self):
        """Fast check for queued interrupt events."""
        return (self._pending_delta != 0) or (self._event_head != self._event_tail)

    def inject(self, *events):
        """Desktop test helper."""
        for event in events:
            if event == "cw":
                self._pending_delta += 1
            elif event == "ccw":
                self._pending_delta -= 1
            elif event == "long":
                self.state.button_was_long = True
                self._queue_event_code(self._EVT_LONG)
            elif event == "click":
                self.state.button_was_long = False
                self._queue_event_code(self._EVT_CLICK)
        return list(events)
