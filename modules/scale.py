"""Scale math and sensor wrapper logic."""

import json

from config import (
    CALIBRATION_FILE,
    DEFAULT_SCALE_FACTOR,
    DEFAULT_TARE_OFFSET,
    EMA_ALPHA,
    HX711_SAMPLES,
    STABLE_TOLERANCE_KG,
    STABLE_WINDOW,
    UNSTABLE_TOLERANCE_KG,
    WEIGHT_CORRECTION_FACTOR,
    WEIGHT_DECIMALS,
)


def load_calibration():
    """Load calibration data from file. Returns (offset, scale_factor) or defaults.

    scale_factor is expected to be calibrated against g=1 base mass.
    """
    try:
        with open(CALIBRATION_FILE, "r") as f:
            data = json.load(f)
            return data.get("offset", DEFAULT_TARE_OFFSET), data.get("scale_factor", DEFAULT_SCALE_FACTOR)
    except (OSError, ValueError):
        return DEFAULT_TARE_OFFSET, DEFAULT_SCALE_FACTOR


def save_calibration(offset, scale_factor):
    """Save calibration data to file.

    base_g is stored for clarity/debugging: all scale factors are g=1 based.
    """
    data = {"offset": offset, "scale_factor": scale_factor, "base_g": 1.0}
    with open(CALIBRATION_FILE, "w") as f:
        json.dump(data, f)


class ScaleMath:
    def raw_to_kg(self, raw, offset=DEFAULT_TARE_OFFSET, scale_factor=DEFAULT_SCALE_FACTOR):
        if not scale_factor:
            raise ValueError("scale_factor must not be zero")
        value = (raw - offset) / float(scale_factor)
        value = value * WEIGHT_CORRECTION_FACTOR  # Hardware correction
        return round(value, WEIGHT_DECIMALS)

    def median(self, values):
        """Return median of values list."""
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0
        return sorted_vals[mid]

    def moving_average(self, values):
        """Return simple moving average of values."""
        if not values:
            return 0.0
        return sum(values) / len(values)

    def variance(self, values):
        """Return variance (spread) of values."""
        if len(values) < 2:
            return 0.0
        avg = self.moving_average(values)
        return sum((v - avg) ** 2 for v in values) / len(values)

    def stability_level(self, values):
        """Return stability level: 'stable' (green), 'settling' (yellow), 'unstable' (red)."""
        if len(values) < 3:
            return "unstable"
        spread = max(values) - min(values)
        if spread <= STABLE_TOLERANCE_KG:
            return "stable"
        elif spread <= UNSTABLE_TOLERANCE_KG:
            return "settling"
        else:
            return "unstable"

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
        self._ema_value = None

    def read_raw(self):
        return self.adc.read_average(self.samples)

    def tare(self, samples=None):
        count = samples or self.samples
        self.offset = self.adc.read_average(count)
        self._history.clear()
        self._ema_value = None
        return self.offset

    def calibrate(self, known_weight_kg, raw_value=None):
        raw_value = self.read_raw() if raw_value is None else raw_value
        if not known_weight_kg:
            raise ValueError("known_weight_kg must not be zero")
        self.scale_factor = (raw_value - self.offset) / float(known_weight_kg)
        return self.scale_factor

    def read_kg(self):
        """Read raw value and update history."""
        raw = self.read_raw()
        value = self.math.raw_to_kg(raw, self.offset, self.scale_factor)
        self._history.append(value)
        if len(self._history) > STABLE_WINDOW:
            self._history.pop(0)
        
        # Update EMA
        if self._ema_value is None:
            self._ema_value = value
        else:
            self._ema_value = EMA_ALPHA * value + (1 - EMA_ALPHA) * self._ema_value
        
        return value

    def read_filtered_kg(self):
        """Get the best filtered weight value using median + EMA."""
        self.read_kg()
        
        if len(self._history) < 3:
            return round(self._ema_value or 0.0, WEIGHT_DECIMALS)
        
        # Use median to reject outliers, then blend with EMA for smoothness
        median_val = self.math.median(self._history)
        if self._ema_value is not None:
            # Weighted blend: 60% median (outlier rejection), 40% EMA (smoothness)
            blended = 0.6 * median_val + 0.4 * self._ema_value
        else:
            blended = median_val
        
        return round(blended, WEIGHT_DECIMALS)

    def get_moving_average(self):
        """Get simple moving average of history."""
        return round(self.math.moving_average(self._history), WEIGHT_DECIMALS)

    def get_median(self):
        """Get median of history."""
        return round(self.math.median(self._history), WEIGHT_DECIMALS)

    def get_ema(self):
        """Get exponential moving average value."""
        if self._ema_value is None:
            return 0.0
        return round(self._ema_value, WEIGHT_DECIMALS)

    def stability_level(self):
        """Get stability level: 'stable', 'settling', or 'unstable'."""
        return self.math.stability_level(self._history)

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
