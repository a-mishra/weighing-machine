"""Screen rendering helpers with graphics for landscape mode."""

from config import DEFAULT_ACTIONS
from modules.lang import tr


class DisplayUI:
    # Darker base theme with white text and high-contrast highlight colors
    BG = 0x0004          # Very dark blue-teal background
    PANEL_BG = 0x0028    # Dark panel background
    ACCENT_DIM = 0x014C  # Selected button fill (dark teal)

    # Core text
    FG = 0xFFFF          # White primary text
    GRAY = 0xDEFB        # Soft white for secondary text
    ACCENT = 0xFFE0      # Yellow accent for focus/selection

    # Status colors
    SUCCESS = 0x07E0     # Green
    WARN = 0xFD20        # Orange
    ERROR = 0xF81F       # Magenta-red
    INFO = 0x07FF        # Cyan info

    # "Popping" value colors
    WEIGHT_COLOR = 0x07FF   # Bright cyan for weight number
    PROFILE_COLOR = 0xF81F  # Bright pink for profile name
    GVALUE_COLOR = 0xFFE0   # Bright yellow for g-value

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

    def _draw_icon_back(self, x, y, color):
        """Draw back arrow icon."""
        self.display.triangle(x, y + 5, x + 6, y, x + 6, y + 10, color, filled=True)
        self.display.fill_rect(x + 5, y + 3, 6, 4, color)

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

    def _draw_status_indicator(self, x, y, stability_level):
        """Draw status LED indicator based on stability level."""
        if stability_level == "locked":
            color = self.SUCCESS  # Green (locked)
            # Draw double ring for locked state
            self.display.circle(x, y, 5, color, filled=True)
            self.display.circle(x, y, 6, self.FG, filled=False)
            self.display.circle(x, y, 7, color, filled=False)
            return
        elif stability_level == "stable":
            color = self.SUCCESS  # Green
        elif stability_level == "settling":
            color = self.WARN     # Yellow
        else:
            color = self.ERROR    # Red
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

    def draw_live(self, language, weight_kg, profile_name, g_value, stability_level, status, action_index=0):
        self._clear()
        
        # Top bar with title and status LED (height: 16px, y: 0-16)
        self.display.fill_rect(0, 0, self.w, 16, self.PANEL_BG)
        self.display.text(tr(language, "title")[:16], 4, 4, self.FG)
        self._draw_status_indicator(self.w - 12, 8, stability_level)
        
        # Weight display group (height: 48px, y: 18-66)
        # Row 1: Large weight value (20px tall) + kg (2x scaled, rightmost)
        weight_str = "%.2f" % weight_kg
        self._draw_large_number(6, 20, weight_str, self.WEIGHT_COLOR)
        self._draw_big_text(self.w - 26, 23, "kg", self.GRAY, scale=2)  # 2x scaled kg (14px tall)
        
        # Row 2: Stability status text with matching color
        if stability_level == "locked":
            self.display.text("LOCKED", 6, 46, self.SUCCESS)
        elif stability_level == "stable":
            self.display.text("Stable", 6, 46, self.SUCCESS)
        elif stability_level == "settling":
            self.display.text("Settling..", 6, 46, self.WARN)
        else:
            self.display.text("Measuring..", 6, 46, self.ERROR)
        
        # Divider after weight
        self.display.hline(4, 60, self.w - 8, self.GRAY)
        
        # Profile and status info (height: 28px, y: 64-92)
        self.display.fill_rect(4, 64, self.w - 8, 28, self.PANEL_BG)
        self.display.text("P:", 8, 68, self.ACCENT)
        self.display.text(profile_name[:8], 28, 68, self.PROFILE_COLOR)
        self.display.text("g=%.1f" % g_value, 100, 68, self.GVALUE_COLOR)
        
        # Status message on second line of panel
        if stability_level in ("stable", "locked"):
            status_color = self.SUCCESS
        elif stability_level == "settling":
            status_color = self.WARN
        elif "ok" in status.lower() or "saved" in status.lower():
            status_color = self.SUCCESS
        else:
            status_color = self.INFO
        self.display.text(status[:18], 8, 80, status_color)
        
        # Divider before action bar (removes gap, adds line)
        self.display.hline(0, 99, self.w, self.GRAY)
        
        # Compact action bar at bottom
        self._draw_action_bar(language, action_index)
        
        self.display.show()

    def _draw_action_bar(self, language, action_index):
        """Draw compact bottom action bar - text for most, icon for menu."""
        bar_y = self.h - 28  # y=100 for 128px screen
        margin = 2  # Left and right margin
        gap = 2     # Gap between buttons
        
        self.display.fill_rect(0, bar_y, self.w, 28, self.PANEL_BG)
        self.display.hline(0, bar_y, self.w, self.GRAY)
        
        num_actions = len(DEFAULT_ACTIONS)
        total_gaps = gap * (num_actions - 1)  # Gaps between buttons
        bar_width = self.w - (margin * 2) - total_gaps  # Usable width after margins and gaps

        # Give profile button extra width so "Profile" fits inside selected box.
        widths = []
        if num_actions == 3 and "profile" in DEFAULT_ACTIONS:
            profile_idx = DEFAULT_ACTIONS.index("profile")
            profile_w = 64  # 7 chars * 8px + breathing room
            other_total = bar_width - profile_w
            base_other = other_total // 2
            widths = [base_other, base_other, base_other]
            widths[profile_idx] = profile_w
            # absorb remainder on the last button
            widths[-1] += bar_width - sum(widths)
        else:
            btn_w = bar_width // num_actions
            widths = [btn_w] * num_actions
            widths[-1] += bar_width - sum(widths)
        
        x = margin
        for i, action in enumerate(DEFAULT_ACTIONS):
            btn_w = widths[i]
            is_selected = (i == action_index)
            
            # Selected button highlight
            if is_selected:
                self.display.fill_rect(x, bar_y + 2, btn_w, 24, self.ACCENT_DIM)
                self.display.rect(x, bar_y + 2, btn_w, 24, self.ACCENT)
            
            color = self.FG if is_selected else self.GRAY
            
            if action == "menu":
                # Draw hamburger menu icon (3 horizontal lines)
                icon_x = x + (btn_w - 16) // 2
                icon_y = bar_y + 6
                self.display.fill_rect(icon_x, icon_y, 16, 3, color)
                self.display.fill_rect(icon_x, icon_y + 5, 16, 3, color)
                self.display.fill_rect(icon_x, icon_y + 10, 16, 3, color)
            else:
                # Text label centered (max 7 chars)
                label = tr(language, action)[:7]
                text_x = x + (btn_w - len(label) * 8) // 2
                self.display.text(label, text_x, bar_y + 10, color)
            x += btn_w + gap

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
            is_back = (idx == 0)  # First item is always "Back"
            
            if is_selected:
                self.display.fill_rect(4, y, self.w - 12, 16, self.ACCENT_DIM)
                self.display.rect(4, y, self.w - 12, 16, self.ACCENT)
                if is_back:
                    self._draw_icon_back(8, y + 3, self.ACCENT)
                else:
                    self.display.triangle(8, y + 4, 8, y + 12, 14, y + 8, self.ACCENT, filled=True)
                self.display.text(item[:14], 22, y + 4, self.FG)
            else:
                if is_back:
                    self._draw_icon_back(8, y + 3, self.GRAY)
                    self.display.text(item[:14], 22, y + 4, self.GRAY)
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

    def draw_profile_list(self, language, items, selected_index):
        """Draw profile selection list."""
        self._clear()
        
        # Title bar (14px)
        self.display.fill_rect(0, 0, self.w, 14, self.PANEL_BG)
        self._draw_icon_profile(4, 1, self.ACCENT)
        self.display.text(tr(language, "select_profile"), 22, 3, self.FG)
        
        # Profile list with back option as first item
        visible_items = 6
        start_idx = max(0, min(selected_index - 2, len(items) - visible_items))
        
        for i, idx in enumerate(range(start_idx, min(start_idx + visible_items, len(items)))):
            y = 18 + i * 18
            is_back = (idx == 0 and items[idx] == "__back__")
            name = tr(language, "back") if is_back else items[idx]
            is_selected = (idx == selected_index)
            
            if is_selected:
                self.display.fill_rect(4, y, self.w - 12, 16, self.ACCENT_DIM)
                self.display.rect(4, y, self.w - 12, 16, self.ACCENT)
                if is_back:
                    self._draw_icon_back(8, y + 3, self.ACCENT)
                else:
                    self.display.triangle(8, y + 4, 8, y + 12, 14, y + 8, self.ACCENT, filled=True)
                self.display.text(name[:14], 22, y + 4, self.FG)
            else:
                if is_back:
                    self._draw_icon_back(8, y + 3, self.GRAY)
                self.display.text(name[:14], 22, y + 4, self.GRAY)
        
        # Scroll indicator
        if len(items) > visible_items:
            list_h = visible_items * 18
            bar_h = max(10, (list_h * visible_items) // len(items))
            bar_y = 18 + (selected_index * (list_h - bar_h)) // max(1, len(items) - 1)
            self.display.fill_rect(self.w - 4, 18, 2, list_h, self.GRAY)
            self.display.fill_rect(self.w - 4, bar_y, 2, bar_h, self.ACCENT)
        
        # Hint bar
        self.display.fill_rect(0, self.h - 14, self.w, 14, self.PANEL_BG)
        self.display.text("Click:Select Long:Back", 6, self.h - 10, self.GRAY)
        
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

    def draw_confirm_delete(self, language, profile_name, option_index):
        """Draw delete confirmation screen."""
        self._clear()
        
        # Title bar
        self.display.fill_rect(0, 0, self.w, 14, self.PANEL_BG)
        self.display.text(tr(language, "confirm_delete"), 6, 3, self.WARN)
        
        # Profile name being deleted
        self.display.text(profile_name[:16], 10, 28, self.FG)
        
        # Yes/No options
        yes_text = tr(language, "yes")
        no_text = tr(language, "no")
        
        btn_w = 60
        btn_h = 24
        gap = 20
        start_x = (self.w - (btn_w * 2 + gap)) // 2
        btn_y = 50
        
        # Yes button
        if option_index == 0:
            self.display.fill_rect(start_x, btn_y, btn_w, btn_h, self.ERROR)
            self.display.rect(start_x, btn_y, btn_w, btn_h, self.WARN)
            self.display.text(yes_text, start_x + (btn_w - len(yes_text) * 8) // 2, btn_y + 8, self.FG)
        else:
            self.display.rect(start_x, btn_y, btn_w, btn_h, self.GRAY)
            self.display.text(yes_text, start_x + (btn_w - len(yes_text) * 8) // 2, btn_y + 8, self.GRAY)
        
        # No button
        no_x = start_x + btn_w + gap
        if option_index == 1:
            self.display.fill_rect(no_x, btn_y, btn_w, btn_h, self.ACCENT_DIM)
            self.display.rect(no_x, btn_y, btn_w, btn_h, self.ACCENT)
            self.display.text(no_text, no_x + (btn_w - len(no_text) * 8) // 2, btn_y + 8, self.FG)
        else:
            self.display.rect(no_x, btn_y, btn_w, btn_h, self.GRAY)
            self.display.text(no_text, no_x + (btn_w - len(no_text) * 8) // 2, btn_y + 8, self.GRAY)
        
        # Hint bar
        self.display.fill_rect(0, self.h - 18, self.w, 18, self.PANEL_BG)
        self.display.text("Rotate:Select Click:OK", 6, self.h - 12, self.GRAY)
        
        self.display.show()

    def draw_calibrate_tare(self, language, raw_value):
        """Draw calibration tare screen - ask user to empty scale."""
        self._clear()
        
        # Title bar
        self.display.fill_rect(0, 0, self.w, 14, self.PANEL_BG)
        self.display.text(tr(language, "calibrate"), 6, 3, self.ACCENT)
        
        # Instruction
        self.display.text(tr(language, "cal_tare"), 10, 24, self.FG)
        
        # Raw value display
        self.display.fill_rect(8, 42, self.w - 16, 28, self.PANEL_BG)
        self.display.text(tr(language, "cal_raw") + ":", 12, 48, self.GRAY)
        self.display.text(str(int(raw_value)), 60, 48, self.ACCENT)
        
        # Hint bar
        self.display.fill_rect(0, self.h - 18, self.w, 18, self.PANEL_BG)
        self.display.text("Click:OK  Long:Cancel", 8, self.h - 12, self.GRAY)
        
        self.display.show()

    def draw_calibrate_place(self, language, raw_value, weight_num):
        """Draw calibration place weight screen."""
        self._clear()
        
        # Title bar
        self.display.fill_rect(0, 0, self.w, 14, self.PANEL_BG)
        title = tr(language, "cal_weight_n") + str(weight_num)
        self.display.text(title, 6, 3, self.ACCENT)
        
        # Instruction
        self.display.text(tr(language, "cal_place"), 10, 24, self.FG)
        
        # Raw value display
        self.display.fill_rect(8, 42, self.w - 16, 28, self.PANEL_BG)
        self.display.text(tr(language, "cal_raw") + ":", 12, 48, self.GRAY)
        self.display.text(str(int(raw_value)), 60, 48, self.ACCENT)
        
        # Hint bar
        self.display.fill_rect(0, self.h - 18, self.w, 18, self.PANEL_BG)
        self.display.text("Click:OK  Long:Cancel", 8, self.h - 12, self.GRAY)
        
        self.display.show()

    def draw_calibrate_input(self, language, weight_kg, weight_num):
        """Draw calibration weight input screen."""
        self._clear()
        
        # Title bar
        self.display.fill_rect(0, 0, self.w, 14, self.PANEL_BG)
        title = tr(language, "cal_input")
        self.display.text(title, 6, 3, self.ACCENT)
        
        # Weight number indicator
        self.display.text(tr(language, "cal_weight_n") + str(weight_num), 10, 24, self.GRAY)
        
        # Large weight value
        weight_str = "%.2f" % weight_kg
        self._draw_large_number(20, 42, weight_str, self.ACCENT)
        self._draw_big_text(self.w - 30, 50, "kg", self.GRAY, scale=2)
        
        # Hint bar
        self.display.fill_rect(0, self.h - 18, self.w, 18, self.PANEL_BG)
        self.display.text("Rotate:+-  Click:OK", 12, self.h - 12, self.GRAY)
        
        self.display.show()

    def draw_calibrate_confirm(self, language, option_index, num_points):
        """Draw calibration confirm screen - add more weights?"""
        self._clear()
        
        # Title bar
        self.display.fill_rect(0, 0, self.w, 14, self.PANEL_BG)
        self.display.text(tr(language, "cal_more"), 6, 3, self.ACCENT)
        
        # Points collected info
        self.display.text("Points: " + str(num_points), 10, 24, self.GRAY)
        
        # Yes/No options
        yes_text = tr(language, "yes")
        no_text = tr(language, "no")
        
        btn_w = 60
        btn_h = 24
        gap = 20
        start_x = (self.w - (btn_w * 2 + gap)) // 2
        btn_y = 50
        
        # Yes button
        if option_index == 0:
            self.display.fill_rect(start_x, btn_y, btn_w, btn_h, self.ACCENT_DIM)
            self.display.rect(start_x, btn_y, btn_w, btn_h, self.ACCENT)
            self.display.text(yes_text, start_x + (btn_w - len(yes_text) * 8) // 2, btn_y + 8, self.FG)
        else:
            self.display.rect(start_x, btn_y, btn_w, btn_h, self.GRAY)
            self.display.text(yes_text, start_x + (btn_w - len(yes_text) * 8) // 2, btn_y + 8, self.GRAY)
        
        # No button
        no_x = start_x + btn_w + gap
        if option_index == 1:
            self.display.fill_rect(no_x, btn_y, btn_w, btn_h, self.ACCENT_DIM)
            self.display.rect(no_x, btn_y, btn_w, btn_h, self.ACCENT)
            self.display.text(no_text, no_x + (btn_w - len(no_text) * 8) // 2, btn_y + 8, self.FG)
        else:
            self.display.rect(no_x, btn_y, btn_w, btn_h, self.GRAY)
            self.display.text(no_text, no_x + (btn_w - len(no_text) * 8) // 2, btn_y + 8, self.GRAY)
        
        # Hint bar
        self.display.fill_rect(0, self.h - 18, self.w, 18, self.PANEL_BG)
        self.display.text("Rotate:Select Click:OK", 6, self.h - 12, self.GRAY)
        
        self.display.show()

    def draw_calibrate_done(self, language, scale_factor):
        """Draw calibration complete screen."""
        self._clear()
        
        # Title bar
        self.display.fill_rect(0, 0, self.w, 14, self.PANEL_BG)
        self.display.text(tr(language, "cal_done"), 6, 3, self.SUCCESS)
        
        # Success message
        self.display.text("Scale Factor:", 10, 30, self.GRAY)
        self.display.text("%.2f" % scale_factor, 10, 48, self.ACCENT)
        
        # Hint bar
        self.display.fill_rect(0, self.h - 18, self.w, 18, self.PANEL_BG)
        self.display.text("Click to continue", 20, self.h - 12, self.GRAY)
        
        self.display.show()
