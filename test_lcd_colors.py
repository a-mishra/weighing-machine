"""LCD Color Test - Tests color display on ST7735.

Upload this file to Pico and run to test colors.
Press the encoder button to cycle through tests.
"""

import time
from machine import Pin, SPI
import framebuf


# Same pin configuration as main app
TFT_SPI_ID = 0
TFT_SCK_PIN = 18
TFT_MOSI_PIN = 19
TFT_CS_PIN = 17
TFT_DC_PIN = 20
TFT_RST_PIN = 21
TFT_BL_PIN = 16
TFT_WIDTH = 160
TFT_HEIGHT = 128
TFT_ROTATION = 1

# Encoder button for cycling tests
ENCODER_SW_PIN = 12


class ST7735Test:
    def __init__(self):
        self.spi = SPI(TFT_SPI_ID, baudrate=20000000, polarity=0, phase=0,
                       sck=Pin(TFT_SCK_PIN), mosi=Pin(TFT_MOSI_PIN))
        self.cs = Pin(TFT_CS_PIN, Pin.OUT, value=1)
        self.dc = Pin(TFT_DC_PIN, Pin.OUT, value=0)
        self.rst = Pin(TFT_RST_PIN, Pin.OUT, value=1)
        self.bl = Pin(TFT_BL_PIN, Pin.OUT, value=0)
        
        self.width = TFT_WIDTH
        self.height = TFT_HEIGHT
        self.rotation = TFT_ROTATION
        
        self.buffer = bytearray(self.width * self.height * 2)
        self.swap_buffer = bytearray(self.width * self.height * 2)
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)
        
        self.init_display()
    
    def write_cmd(self, cmd):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytes([cmd]))
        self.cs.value(1)
    
    def write_data(self, data):
        self.dc.value(1)
        self.cs.value(0)
        if isinstance(data, int):
            self.spi.write(bytes([data]))
        else:
            self.spi.write(data)
        self.cs.value(1)
    
    def reset(self):
        self.rst.value(1)
        time.sleep_ms(50)
        self.rst.value(0)
        time.sleep_ms(50)
        self.rst.value(1)
        time.sleep_ms(150)
    
    def init_display(self):
        self.reset()
        self.write_cmd(0x01)  # SWRESET
        time.sleep_ms(150)
        self.write_cmd(0x11)  # SLPOUT
        time.sleep_ms(150)
        self.write_cmd(0x3A)
        self.write_data(0x05)  # RGB565
        self.write_cmd(0x36)
        # MADCTL - try changing this value to fix colors
        rotation_map = {0: 0x00, 1: 0x60, 2: 0xC0, 3: 0xA0}
        self.write_data(rotation_map.get(self.rotation, 0x00))
        self.write_cmd(0x20)  # INVOFF
        self.write_cmd(0x29)  # DISPON
        self.bl.value(1)
    
    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(0x2A)
        self.write_data(bytearray([0x00, x0, 0x00, x1]))
        self.write_cmd(0x2B)
        self.write_data(bytearray([0x00, y0, 0x00, y1]))
        self.write_cmd(0x2C)
    
    def show(self):
        self.set_window(0, 0, self.width - 1, self.height - 1)
        # FrameBuffer stores RGB565 in little-endian; LCD expects big-endian.
        buf = self.buffer
        swap = self.swap_buffer
        for i in range(0, len(buf), 2):
            swap[i] = buf[i + 1]
            swap[i + 1] = buf[i]
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(swap)
        self.cs.value(1)
    
    def fill(self, color):
        self.fb.fill(color)
    
    def fill_rect(self, x, y, w, h, color):
        self.fb.fill_rect(x, y, w, h, color)
    
    def text(self, s, x, y, color):
        self.fb.text(s, x, y, color)


def main():
    print("LCD Color Test")
    print("Press encoder button to cycle through tests")
    
    lcd = ST7735Test()
    button = Pin(ENCODER_SW_PIN, Pin.IN, Pin.PULL_UP)
    
    # Define test colors in RGB565 format
    colors = [
        ("RED", 0xF800),       # Pure red
        ("GREEN", 0x07E0),     # Pure green
        ("BLUE", 0x001F),      # Pure blue
        ("YELLOW", 0xFFE0),    # Red + Green
        ("CYAN", 0x07FF),      # Green + Blue
        ("MAGENTA", 0xF81F),   # Red + Blue
        ("WHITE", 0xFFFF),     # All on
        ("BLACK", 0x0000),     # All off
        ("ORANGE", 0xFD20),    # Orange
        ("TEAL", 0x0410),      # Dark cyan/teal
    ]
    
    test_index = 0
    last_button = 1
    
    def show_color_test(index):
        """Show a single color fullscreen with label."""
        name, color = colors[index % len(colors)]
        lcd.fill(color)
        # Draw label with contrasting color
        label_color = 0x0000 if color > 0x7FFF else 0xFFFF
        lcd.text(name, 10, 10, label_color)
        lcd.text("RGB565: 0x%04X" % color, 10, 30, label_color)
        lcd.text("Press btn: next", 10, 100, label_color)
        lcd.show()
        print(f"Showing: {name} = 0x{color:04X}")
    
    def show_color_bars():
        """Show color bars for comparison."""
        lcd.fill(0x0000)
        bar_h = lcd.height // 8
        
        bars = [
            ("RED", 0xF800),
            ("GRN", 0x07E0),
            ("BLU", 0x001F),
            ("YEL", 0xFFE0),
            ("CYN", 0x07FF),
            ("MAG", 0xF81F),
            ("WHT", 0xFFFF),
            ("GRY", 0x7BEF),
        ]
        
        for i, (name, color) in enumerate(bars):
            y = i * bar_h
            lcd.fill_rect(0, y, lcd.width, bar_h, color)
            label_color = 0x0000 if color > 0x7FFF else 0xFFFF
            lcd.text(name, 5, y + 4, label_color)
        
        lcd.show()
        print("Showing color bars")
    
    def show_rgb_test():
        """Show RGB squares side by side."""
        lcd.fill(0x0000)
        w = lcd.width // 3
        
        lcd.fill_rect(0, 20, w, 80, 0xF800)      # Red
        lcd.fill_rect(w, 20, w, 80, 0x07E0)      # Green
        lcd.fill_rect(w*2, 20, w, 80, 0x001F)    # Blue
        
        lcd.text("R", w//2 - 4, 55, 0xFFFF)
        lcd.text("G", w + w//2 - 4, 55, 0x0000)
        lcd.text("B", w*2 + w//2 - 4, 55, 0xFFFF)
        
        lcd.text("RGB Test", 50, 5, 0xFFFF)
        lcd.text("Should show:", 30, 105, 0xFFFF)
        lcd.text("RED GRN BLU", 35, 115, 0xFFFF)
        
        lcd.show()
        print("Showing RGB test - should be Red, Green, Blue left to right")
    
    # Test sequence
    tests = [
        show_rgb_test,
        show_color_bars,
    ] + [lambda i=i: show_color_test(i) for i in range(len(colors))]
    
    current_test = 0
    tests[current_test]()
    
    print("\nIf colors are wrong:")
    print("- RED shows as BLUE: swap RGB/BGR in driver")
    print("- Colors inverted: toggle INVON/INVOFF in driver")
    print("- TEAL shows as VIOLET: Red and Blue are swapped")
    
    while True:
        button_state = button.value()
        
        if button_state == 0 and last_button == 1:
            time.sleep_ms(50)  # Debounce
            if button.value() == 0:
                current_test = (current_test + 1) % len(tests)
                tests[current_test]()
        
        last_button = button_state
        time.sleep_ms(10)


if __name__ == "__main__":
    main()
