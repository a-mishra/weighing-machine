"""Small ST7735 framebuffer-based driver.

This is intentionally compact and aimed at a common 128x160 SPI module.
"""

try:
    from machine import Pin, SPI  # type: ignore
except ImportError:  # pragma: no cover
    Pin = None
    SPI = None

try:
    import framebuf  # type: ignore
except ImportError:  # pragma: no cover
    framebuf = None

try:
    from utime import sleep_ms  # type: ignore
except ImportError:  # pragma: no cover
    from time import sleep as _sleep

    def sleep_ms(value):
        _sleep(value / 1000.0)


class ST7735:
    def __init__(
        self,
        width,
        height,
        spi=None,
        cs=None,
        dc=None,
        rst=None,
        bl=None,
        rotation=0,
    ):
        self.width = width
        self.height = height
        self.rotation = rotation
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.bl = bl
        self._is_stub = framebuf is None or spi is None
        if not self._is_stub:
            self.buffer = bytearray(self.width * self.height * 2)
            self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)
            self.init_display()
        else:
            self.buffer = bytearray()
            self.fb = None

    def color565(self, red, green, blue):
        return ((red & 0xF8) << 8) | ((green & 0xFC) << 3) | (blue >> 3)

    def write_cmd(self, command):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytearray([command]))
        self.cs.value(1)

    def write_data(self, data):
        self.dc.value(1)
        self.cs.value(0)
        if isinstance(data, int):
            data = bytearray([data])
        self.spi.write(data)
        self.cs.value(1)

    def reset(self):
        if self.rst is None:
            return
        self.rst.value(1)
        sleep_ms(50)
        self.rst.value(0)
        sleep_ms(50)
        self.rst.value(1)
        sleep_ms(150)

    def init_display(self):
        self.reset()
        self.write_cmd(0x01)  # SWRESET
        sleep_ms(150)
        self.write_cmd(0x11)  # SLPOUT
        sleep_ms(150)
        self.write_cmd(0x3A)
        self.write_data(0x05)  # RGB565
        self.write_cmd(0x36)
        rotation_map = {0: 0x00, 1: 0x60, 2: 0xC0, 3: 0xA0}
        self.write_data(rotation_map.get(self.rotation, 0x00))
        self.write_cmd(0x21)  # INVON
        self.write_cmd(0x29)  # DISPON
        if self.bl is not None:
            self.bl.value(1)
        self.fill(0)
        self.show()

    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(0x2A)
        self.write_data(bytearray([0x00, x0, 0x00, x1]))
        self.write_cmd(0x2B)
        self.write_data(bytearray([0x00, y0, 0x00, y1]))
        self.write_cmd(0x2C)

    def fill(self, color):
        if self.fb:
            self.fb.fill(color)

    def text(self, text, x, y, color):
        if self.fb:
            self.fb.text(str(text), int(x), int(y), color)

    def fill_rect(self, x, y, w, h, color):
        if self.fb:
            self.fb.fill_rect(int(x), int(y), int(w), int(h), color)

    def rect(self, x, y, w, h, color):
        if self.fb:
            self.fb.rect(int(x), int(y), int(w), int(h), color)

    def hline(self, x, y, w, color):
        if self.fb:
            self.fb.hline(int(x), int(y), int(w), color)

    def vline(self, x, y, h, color):
        if self.fb:
            self.fb.vline(int(x), int(y), int(h), color)

    def pixel(self, x, y, color):
        if self.fb:
            self.fb.pixel(int(x), int(y), color)

    def line(self, x0, y0, x1, y1, color):
        if self.fb:
            self.fb.line(int(x0), int(y0), int(x1), int(y1), color)

    def circle(self, cx, cy, r, color, filled=False):
        if not self.fb:
            return
        x, y, d = r, 0, 1 - r
        while x >= y:
            if filled:
                self.hline(cx - x, cy + y, 2 * x + 1, color)
                self.hline(cx - x, cy - y, 2 * x + 1, color)
                self.hline(cx - y, cy + x, 2 * y + 1, color)
                self.hline(cx - y, cy - x, 2 * y + 1, color)
            else:
                pts = [(cx+x,cy+y),(cx-x,cy+y),(cx+x,cy-y),(cx-x,cy-y),
                       (cx+y,cy+x),(cx-y,cy+x),(cx+y,cy-x),(cx-y,cy-x)]
                for px, py in pts:
                    self.pixel(px, py, color)
            y += 1
            if d < 0:
                d += 2 * y + 1
            else:
                x -= 1
                d += 2 * (y - x) + 1

    def triangle(self, x0, y0, x1, y1, x2, y2, color, filled=False):
        if not self.fb:
            return
        if filled:
            def sort_y(a, b, c):
                if a[1] > b[1]: a, b = b, a
                if a[1] > c[1]: a, c = c, a
                if b[1] > c[1]: b, c = c, b
                return a, b, c
            p0, p1, p2 = sort_y((x0,y0), (x1,y1), (x2,y2))
            def interp(y, pa, pb):
                if pb[1] == pa[1]: return pa[0]
                return pa[0] + (pb[0] - pa[0]) * (y - pa[1]) // (pb[1] - pa[1])
            for y in range(p0[1], p2[1] + 1):
                if y < p1[1]:
                    xa = interp(y, p0, p1)
                    xb = interp(y, p0, p2)
                else:
                    xa = interp(y, p1, p2)
                    xb = interp(y, p0, p2)
                if xa > xb: xa, xb = xb, xa
                self.hline(xa, y, xb - xa + 1, color)
        else:
            self.line(x0, y0, x1, y1, color)
            self.line(x1, y1, x2, y2, color)
            self.line(x2, y2, x0, y0, color)

    def rounded_rect(self, x, y, w, h, r, color, filled=False):
        if not self.fb:
            return
        if filled:
            self.fill_rect(x + r, y, w - 2*r, h, color)
            self.fill_rect(x, y + r, r, h - 2*r, color)
            self.fill_rect(x + w - r, y + r, r, h - 2*r, color)
            for cx, cy in [(x+r, y+r), (x+w-r-1, y+r), (x+r, y+h-r-1), (x+w-r-1, y+h-r-1)]:
                self.circle(cx, cy, r, color, filled=True)
        else:
            self.hline(x + r, y, w - 2*r, color)
            self.hline(x + r, y + h - 1, w - 2*r, color)
            self.vline(x, y + r, h - 2*r, color)
            self.vline(x + w - 1, y + r, h - 2*r, color)

    def show(self):
        if self._is_stub:
            return
        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.write_data(self.buffer)


def create_default_display(config_module):
    if Pin is None or SPI is None:
        return ST7735(config_module.TFT_WIDTH, config_module.TFT_HEIGHT)

    spi = SPI(
        config_module.TFT_SPI_ID,
        baudrate=20_000_000,
        polarity=0,
        phase=0,
        sck=Pin(config_module.TFT_SCK_PIN),
        mosi=Pin(config_module.TFT_MOSI_PIN),
    )
    return ST7735(
        config_module.TFT_WIDTH,
        config_module.TFT_HEIGHT,
        spi=spi,
        cs=Pin(config_module.TFT_CS_PIN, Pin.OUT),
        dc=Pin(config_module.TFT_DC_PIN, Pin.OUT),
        rst=Pin(config_module.TFT_RST_PIN, Pin.OUT),
        bl=Pin(config_module.TFT_BL_PIN, Pin.OUT),
        rotation=config_module.TFT_ROTATION,
    )
