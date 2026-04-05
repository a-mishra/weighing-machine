"""Desktop simulation and on-device encoder event logger."""

import time
import sys

sys.path.insert(0, "/lib")
sys.path.insert(0, "")

import config
from modules.encoder import RotaryEncoder


def main():
    encoder = RotaryEncoder(config.ENCODER_CLK_PIN, config.ENCODER_DT_PIN, config.ENCODER_SW_PIN)
    hardware = not getattr(encoder, "_mock_mode", False)

    if not hardware:
        events = encoder.inject("cw", "cw", "ccw", "click", "long")
        print("Simulated encoder events:", events, "position=", encoder.state.position)
        return

    print("Encoder test using micropython-rotary library")
    print("CLK=GP{} DT=GP{} SW=GP{}".format(
        config.ENCODER_CLK_PIN, config.ENCODER_DT_PIN, config.ENCODER_SW_PIN))
    print("Rotate or press the encoder. Ctrl+C to stop.")
    print("-" * 40)
    
    last_pos = encoder.state.position
    while True:
        try:
            events = encoder.poll()
            if events:
                print("events:", events, "position=", encoder.state.position)
            elif encoder.state.position != last_pos:
                print("position=", encoder.state.position)
                last_pos = encoder.state.position
            time.sleep(0.02)
        except KeyboardInterrupt:
            break
    
    print("\nFinal position:", encoder.state.position)


if __name__ == "__main__":
    main()
