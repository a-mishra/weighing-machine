"""Screen rendering helpers with graphics for landscape mode."""

from config import DEFAULT_ACTIONS
from modules.lang import tr


class DisplayUI:
    # Dark theme with high contrast
    BG = 0x0000          # Black background
    FG = 0xFFFF          # White text
    ACCENT = 0x07FF      # Cyan accent
    ACCENT_DIM = 0x0410  # Dark cyan
    SUCCESS = 0x07E0     # Green
    WARN = 0xFBE0        # Yellow/Orange
    ERROR = 0xF800       # Red
    INFO = 0x001F        # Blue
    GRAY = 0x8410        # Gray for inactive elements
    PANEL_BG = 0x1082    # Dark gray panel background

    def __init__(self, display):
        self.display = display
        self.w = display.width
        self.h = display.height

    def _clear(self):
        self.display.fill(self.BG)

    def _draw_icon_scale(self, x, y, color):
        """Draw a scale/weight icon."""
        self.display.fill_rect(x, y + 8, 16, 3, color)
        self.display.triangle(x + 8, y, x + 2, y + 8, x + 14, y + 8, color, filled=True)
        self.display.fill_rect(x + 2, y + 11, 12, 2, color)

    def _draw_icon_menu(self, x, y, color):
        """Draw hamburger menu icon."""
        for i in range(3):
            self.display.fill_rect(x, y + i * 5, 14, 3, color)

    def _draw_icon_tare(self, x, y, color):
        """Draw tare/zero icon."""
        self.display.circle(x + 7, y + 7, 7, color, filled=False)
        self.display.text("0", x + 4, y + 3, color)

    def _draw_icon_profile(self, x, y, color):
        """Draw profile/user icon."""
        self.display.circle(x + 7, y + 4, 4, color, filled=True)
        self.display.fill_rect(x + 2, y + 9, 11, 6, color)

    def _draw_icon_send(self, x, y, color):
        """Draw send/upload icon."""
        self.display.triangle(x + 7, y, x + 2, y + 8, x + 12, y + 8, color, filled=True)
        self.display.fill_rect(x + 5, y + 8, 5, 6, color)

    def _draw_icon_check(self, x, y, color):
        """Draw checkmark icon."""
        self.display.line(x, y + 6, x + 4, y + 10, color)
        self.display.line(x + 4, y + 10, x + 12, y + 2, color)

    def _draw_icon_warning(self, x, y, color):
        """Draw warning triangle icon."""
        self.display.triangle(x + 7, y, x, y + 12, x + 14, y + 12, color, filled=False)
        self.display.text("!", x + 5, y + 4, color)

    def _draw_status_indicator(self, x, y, stable):
        """Draw status LED indicator."""
        color = self.SUCCESS if stable else self.WARN
        self.display.circle(x, y, 5, color, filled=True)
        self.display.circle(x, y, 6, self.FG, filled=False)

    def _draw_large_digit(self, x, y, digit, color):
        """Draw a large digit (0-9 or '.') - 12px wide x 20px tall, well-proportioned."""
        t = 3  # thickness
        w = 12  # width
        h = 20  # height
        
        # 7-segment style: top, top-left, top-right, middle, bot-left, bot-right, bottom
        segs = {
            '0': ['top', 'tl', 'tr', 'bl', 'br', 'bot'],
            '1': ['tr', 'br'],
            '2': ['top', 'tr', 'mid', 'bl', 'bot'],
            '3': ['top', 'tr', 'mid', 'br', 'bot'],
            '4': ['tl', 'tr', 'mid', 'br'],
            '5': ['top', 'tl', 'mid', 'br', 'bot'],
            '6': ['top', 'tl', 'mid', 'bl', 'br', 'bot'],
            '7': ['top', 'tr', 'br'],
            '8': ['top', 'tl', 'tr', 'mid', 'bl', 'br', 'bot'],
            '9': ['top', 'tl', 'tr', 'mid', 'br', 'bot'],
            '.': ['dot'],
            '-': ['mid'],
            'k': ['tl', 'bl', 'k1', 'k2'],  # k shape
            'g': ['top', 'tl', 'mid', 'bl', 'br', 'bot'],  # like 6
        }
        
        seg_coords = {
            'top': (0, 0, w, t),
            'tl': (0, 0, t, h//2 + t//2),
            'tr': (w - t, 0, t, h//2 + t//2),
            'mid': (0, h//2 - t//2, w, t),
            'bl': (0, h//2 - t//2, t, h//2 + t//2),
            'br': (w - t, h//2 - t//2, t, h//2 + t//2),
            'bot': (0, h - t, w, t),
            'dot': (w//2 - t//2, h - t, t, t),  # Centered at bottom
            'k1': (t + 2, h//2 - t//2 - 3, w - t - 2, t),  # K upper diagonal (simplified as horizontal)
            'k2': (t + 2, h//2 + t//2 + 3, w - t - 2, t),  # K lower diagonal (simplified as horizontal)
        }
        
        for seg in segs.get(digit, []):
            if seg in seg_coords:
                sx, sy, sw, sh = seg_coords[seg]
                self.display.fill_rect(x + sx, y + sy, sw, sh, color)
        
        if digit == '.':
            return 10  # Dot width + extra spacing after
        return w + 3  # return width + spacing for next digit

    def _draw_large_number(self, x, y, text, color):
        """Draw a string of digits at large scale (20px tall)."""
        cursor_x = x
        for char in text:
            cursor_x += self._draw_large_digit(cursor_x, y, char, color)

    def _draw_big_text(self, x, y, text, color, scale=2):
        """Draw text at scaled size (2x = 16px tall, 3x = 24px tall)."""
        # Simple bitmap font for common characters at any scale
        # Each char is 5 wide x 7 tall in the bitmap, scaled by 'scale'
        font = {
            'k': [
                0b10001,
                0b10010,
                0b10100,
                0b11000,
                0b10100,
                0b10010,
                0b10001,
            ],
            'g': [
                0b01110,
                0b10001,
                0b10000,
                0b10111,
                0b10001,
                0b10001,
                0b01110,
            ],
            'K': [
                0b10001,
                0b10010,
                0b10100,
                0b11000,
                0b10100,
                0b10010,
                0b10001,
            ],
            'G': [
                0b01110,
                0b10001,
                0b10000,
                0b10111,
                0b10001,
                0b10001,
                0b01110,
            ],
        }
        
        cursor_x = x
        for char in text:
            if char in font:
                bitmap = font[char]
                for row_idx, row in enumerate(bitmap):
                    for col in range(5):
                        if row & (1 << (4 - col)):
                            self.display.fill_rect(
                                cursor_x + col * scale,
                                y + row_idx * scale,
                                scale, scale, color
                            )
                cursor_x += 6 * scale  # char width + spacing
            else:
                # Fallback to normal text for unknown chars
                self.display.text(char, cursor_x, y, color)
                cursor_x += 8

    def splash(self, language):
        self._clear()
        cx = self.w // 2
        self._draw_icon_scale(cx - 8, 15, self.ACCENT)
        self.display.text(tr(language, "title"), cx - 40, 38, self.FG)
        self.display.text("160x128 Landscape", cx - 64, 55, self.GRAY)
        self.display.text("Pico 2W + HX711", cx - 56, 72, self.ACCENT)
        self.display.rounded_rect(20, 95, self.w - 40, 16, 4, self.ACCENT_DIM, filled=True)
        self.display.text("Loading...", cx - 32, 99, self.FG)
        self.display.show()

    def draw_live(self, language, weight_kg, profile_name, g_value, stable, status, action_index=0):
        self._clear()
        
        # Top bar with title and status LED (height: 16px, y: 0-16)
        self.display.fill_rect(0, 0, self.w, 16, self.PANEL_BG)
        self.display.text(tr(language, "title")[:16], 4, 4, self.FG)
        self._draw_status_indicator(self.w - 12, 8, stable)
        
        # Weight display group (height: 48px, y: 18-66)
        # Row 1: Large weight value (20px tall) + kg (2x scaled, rightmost)
        weight_str = "%.3f" % weight_kg
        self._draw_large_number(6, 20, weight_str, self.ACCENT)
        self._draw_big_text(self.w - 26, 23, "kg", self.GRAY, scale=2)  # 2x scaled kg (14px tall)
        
        # Row 2: Status indicator
        if stable:
            self.display.text("Stable", 6, 46, self.SUCCESS)
        else:
            self.display.text("Measuring..", 6, 46, self.WARN)
        
        # Divider after weight
        self.display.hline(4, 60, self.w - 8, self.GRAY)
        
        # Profile and status info (height: 28px, y: 64-92)
        self.display.fill_rect(4, 64, self.w - 8, 28, self.PANEL_BG)
        self.display.text("P:", 8, 68, self.ACCENT)
        self.display.text(profile_name[:8], 28, 68, self.FG)
        self.display.text("g=%.1f" % g_value, 100, 68, self.GRAY)
        
        # Status message on second line of panel
        status_color = self.SUCCESS if "ok" in status.lower() or "saved" in status.lower() else self.INFO
        self.display.text(status[:18], 8, 80, status_color)
        
        # Divider before action bar (removes gap, adds line)
        self.display.hline(0, 99, self.w, self.GRAY)
        
        # Compact action bar at bottom
        self._draw_action_bar(language, action_index)
        
        self.display.show()

    def _draw_action_bar(self, language, action_index):
        """Draw compact bottom action bar - text for most, icon for menu."""
        bar_y = self.h - 28  # y=100 for 128px screen
        self.display.fill_rect(0, bar_y, self.w, 28, self.PANEL_BG)
        self.display.hline(0, bar_y, self.w, self.GRAY)
        
        btn_w = self.w // len(DEFAULT_ACTIONS)  # Dynamic width based on action count
        
        for i, action in enumerate(DEFAULT_ACTIONS):
            x = i * btn_w
            is_selected = (i == action_index)
            
            # Selected button highlight
            if is_selected:
                self.display.fill_rect(x + 2, bar_y + 2, btn_w - 4, 24, self.ACCENT_DIM)
                self.display.rect(x + 2, bar_y + 2, btn_w - 4, 24, self.ACCENT)
            
            color = self.FG if is_selected else self.GRAY
            
            if action == "menu":
                # Draw hamburger menu icon (3 horizontal lines)
                icon_x = x + (btn_w - 16) // 2
                icon_y = bar_y + 6
                self.display.fill_rect(icon_x, icon_y, 16, 3, color)
                self.display.fill_rect(icon_x, icon_y + 5, 16, 3, color)
                self.display.fill_rect(icon_x, icon_y + 10, 16, 3, color)
            else:
                # Text label centered (max 7 chars for 53px button width)
                label = tr(language, action)[:7]
                text_x = x + (btn_w - len(label) * 8) // 2
                self.display.text(label, text_x, bar_y + 10, color)

    def draw_menu(self, language, items, selected_index, title_key="menu"):
        self._clear()
        
        # Title bar (14px)
        self.display.fill_rect(0, 0, self.w, 14, self.PANEL_BG)
        self._draw_icon_menu(4, 2, self.ACCENT)
        self.display.text(tr(language, title_key), 22, 3, self.FG)
        
        # Menu items (6 visible, 18px each = 108px, fits in 128-14=114px)
        visible_items = 6
        start_idx = max(0, min(selected_index - 2, len(items) - visible_items))
        
        for i, idx in enumerate(range(start_idx, min(start_idx + visible_items, len(items)))):
            y = 18 + i * 18
            item = items[idx]
            is_selected = (idx == selected_index)
            
            if is_selected:
                self.display.fill_rect(4, y, self.w - 12, 16, self.ACCENT_DIM)
                self.display.rect(4, y, self.w - 12, 16, self.ACCENT)
                self.display.triangle(8, y + 4, 8, y + 12, 14, y + 8, self.ACCENT, filled=True)
                self.display.text(item[:16], 18, y + 4, self.FG)
            else:
                self.display.text(item[:16], 18, y + 4, self.GRAY)
        
        # Scroll indicator
        if len(items) > visible_items:
            list_h = visible_items * 18
            bar_h = max(10, (list_h * visible_items) // len(items))
            bar_y = 18 + (selected_index * (list_h - bar_h)) // max(1, len(items) - 1)
            self.display.fill_rect(self.w - 4, 18, 2, list_h, self.GRAY)
            self.display.fill_rect(self.w - 4, bar_y, 2, bar_h, self.ACCENT)
        
        self.display.show()

    def draw_message(self, language, title, line1, line2=""):
        self._clear()
        
        # Title bar (14px)
        self.display.fill_rect(0, 0, self.w, 14, self.PANEL_BG)
        self.display.text(title[:18], 6, 3, self.ACCENT)
        
        # Content box
        self.display.rounded_rect(8, 22, self.w - 16, 44, 4, self.PANEL_BG, filled=True)
        self.display.rounded_rect(8, 22, self.w - 16, 44, 4, self.ACCENT, filled=False)
        
        # Content text
        self.display.text(line1[:18], 16, 32, self.FG)
        if line2:
            self.display.text(line2[:18], 16, 48, self.GRAY)
        
        # Hint bar at bottom
        self.display.fill_rect(0, self.h - 18, self.w, 18, self.PANEL_BG)
        self.display.text("Rotate:Edit Long:Save", 8, self.h - 12, self.GRAY)
        
        self.display.show()
