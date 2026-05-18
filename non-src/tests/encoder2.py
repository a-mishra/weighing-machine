from machine import Pin
import time
clk = Pin(10, Pin.IN, Pin.PULL_UP)
dt = Pin(11, Pin.IN, Pin.PULL_UP)
sw = Pin(12, Pin.IN, Pin.PULL_UP)
print("Rotate encoder slowly and press button...")
print("CLK/DT should toggle 0↔1 when rotating")
print("SW should be 1 (released) or 0 (pressed)")
while True:
    print(f"CLK={clk.value()} DT={dt.value()} SW={sw.value()}")
    time.sleep(0.1)