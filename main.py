"""Main application entry point for the weighing machine."""

import sys
sys.path.insert(0, "/lib")

import time

import config
from drivers.st7735 import create_default_display
from modules.buzzer import Buzzer
from modules.cloud import CloudClient, build_payload
from modules.display_ui import DisplayUI
from modules.encoder import RotaryEncoder
from modules.lang import tr
from modules.profiles import ProfileStore, clamp_g_value
from modules.scale import ScaleSensor, load_calibration, save_calibration

try:
    from drivers.hx711 import HX711
except ImportError:  # pragma: no cover
    HX711 = None


class WeighingMachineApp:
    def __init__(self, store, scale, ui, encoder, buzzer, cloud):
        self.store = store
        self.scale = scale
        self.ui = ui
        self.encoder = encoder
        self.buzzer = buzzer
        self.cloud = cloud

        self.state = "live"
        self.menu_keys = [
            "back",
            "recalibration",
            "language",
        ]
        self.profile_menu_keys = [
            "back",
            "select_profile",
            "create_profile",
            "edit_name",
            "edit_g",
            "delete_profile",
        ]
        self.language_menu_keys = ["back", "english", "hindi"]
        self.menu_index = 0
        self.profile_menu_index = 0
        self.language_menu_index = 0
        self.action_index = 0
        self.status_key = "stable"
        self.current_weight = 0.0
        self.current_mass = 0.0  # g=1.0 calibrated mass value
        self.locked_weight = None
        self.lock_time = 0
        self.stable_count = 0
        self.name_buffer = list("PROFILE   ")
        self.name_position = 0
        self.temp_g = config.DEFAULT_G_VALUE
        self.create_mode = False
        self.charset = config.PROFILE_NAME_CHARSET
        
        # Calibration state
        self.cal_points = []
        self.cal_raw = 0
        self.cal_weight = config.CALIBRATE_DEFAULT_WEIGHT
        self.cal_option = 0
        self.cal_tare_offset = 0
        self.cal_last_rotate = 0  # For fast rotation detection
        self.cal_profile_g = config.DEFAULT_G_VALUE
        
        # Delete confirmation state
        self.delete_option = 1  # Default to "No"
        
        # Profile selection state
        self.profile_list_index = 0
        self.profile_menu_items = []

        # Runtime-editable configuration
        self.runtime_stable_lock_count = config.STABLE_LOCK_COUNT
        self.runtime_stable_freeze_ms = config.STABLE_FREEZE_MS
        self.config_edit_index = 0

    @property
    def language(self):
        return self.store.get_language()

    def active_profile(self):
        return self.store.get_active_profile()

    def _get_time_ms(self):
        """Get current time in milliseconds."""
        try:
            return time.ticks_ms()
        except AttributeError:
            return int(time.time() * 1000)

    def refresh_weight(self):
        now = self._get_time_ms()
        active_g = self.active_profile()["g"]
        
        # Check if we're in frozen state
        if self.locked_weight is not None:
            try:
                elapsed = time.ticks_diff(now, self.lock_time)
            except AttributeError:
                elapsed = now - self.lock_time
            
            if elapsed < self.runtime_stable_freeze_ms:
                # Still frozen - return locked weight
                self.status_key = "locked"
                return self.locked_weight
            else:
                # Freeze expired - unlock
                self.locked_weight = None
                self.stable_count = 0
        
        # Read new weight
        self.current_mass = self.scale.read_filtered_kg()
        self.current_weight = round(self.current_mass * active_g, config.WEIGHT_DECIMALS)
        stability = self.scale.stability_level()
        
        if stability == "stable":
            self.stable_count += 1
            if self.stable_count >= self.runtime_stable_lock_count:
                # Lock the weight
                self.locked_weight = self.current_weight
                self.lock_time = now
                self.status_key = "locked"
                self.buzzer.beep(50)  # Short beep to indicate lock
            else:
                self.status_key = "stable"
        else:
            self.stable_count = 0
            if stability == "settling":
                self.status_key = "settling"
            else:
                self.status_key = "not_ready"
        
        return self.current_weight

    def tare_scale(self):
        self.scale.tare()
        save_calibration(self.scale.offset, self.scale.scale_factor)
        self.status_key = "saved"
        self.buzzer.double_beep()

    def cycle_profile(self):
        profiles = self.store.list_profiles()
        current = self.active_profile()["name"]
        names = [item["name"] for item in profiles]
        idx = (names.index(current) + 1) % len(names)
        self.store.select_profile(names[idx])
        self.locked_weight = None
        self.stable_count = 0
        self.status_key = "saved"
        self.buzzer.beep()

    def toggle_language(self):
        new_language = "hi" if self.language == "en" else "en"
        self.store.set_language(new_language)
        self.status_key = "saved"
        self.buzzer.beep()

    def start_create_profile(self):
        self.create_mode = True
        self.state = "edit_name"
        self.name_buffer = list("PROFILE   ")
        self.name_position = 0
        self.temp_g = config.DEFAULT_G_VALUE

    def start_edit_name(self):
        name = str(self.active_profile()["name"])
        current = (name + (" " * config.PROFILE_NAME_LENGTH))[: config.PROFILE_NAME_LENGTH]
        self.create_mode = False
        self.state = "edit_name"
        self.name_buffer = list(current[: config.PROFILE_NAME_LENGTH])
        self.name_position = 0
        self.temp_g = self.active_profile()["g"]

    def start_edit_g(self):
        self.create_mode = False
        self.state = "edit_g"
        self.temp_g = self.active_profile()["g"]

    def activate_menu(self):
        key = self.menu_keys[self.menu_index]
        if key == "back":
            self.state = "live"
        elif key == "recalibration":
            self.start_calibration()
        elif key == "language":
            self.state = "language_menu"
            self.language_menu_index = 1 if len(self.language_menu_keys) > 1 else 0

    def activate_profile_menu(self):
        key = self.profile_menu_keys[self.profile_menu_index]
        if key == "back":
            self.state = "live"
        elif key == "select_profile":
            self.start_profile_select()
        elif key == "create_profile":
            self.start_create_profile()
        elif key == "edit_name":
            self.start_edit_name()
        elif key == "edit_g":
            self.start_edit_g()
        elif key == "delete_profile":
            self.start_delete_profile()

    def activate_language_menu(self):
        key = self.language_menu_keys[self.language_menu_index]
        if key == "back":
            self.state = "menu"
        elif key == "english":
            self.store.set_language("en")
            self.status_key = "saved"
            self.buzzer.beep()
            self.state = "live"
        elif key == "hindi":
            self.store.set_language("hi")
            self.status_key = "saved"
            self.buzzer.beep()
            self.state = "live"

    def start_profile_select(self):
        """Open profile selection list."""
        profiles = self.store.list_profiles()
        active_name = self.active_profile()["name"]
        self.profile_menu_items = ["__back__"] + [p["name"] for p in profiles]
        self.profile_list_index = 0
        for i, p in enumerate(profiles):
            if p["name"] == active_name:
                self.profile_list_index = i + 1
                break
        self.state = "select_profile"
        self.buzzer.beep()

    def select_profile_at_index(self):
        """Select the profile at current list index."""
        if not self.profile_menu_items:
            self.state = "live"
            return

        # First item is back navigation
        if self.profile_list_index == 0:
            self.state = "profile_menu"
            self.buzzer.beep()
            return

        profile_name = self.profile_menu_items[self.profile_list_index]
        self.store.select_profile(profile_name)
        self.locked_weight = None
        self.stable_count = 0
        self.status_key = "saved"
        self.buzzer.double_beep()
        self.state = "live"

    def start_delete_profile(self):
        """Start delete profile confirmation."""
        self.delete_option = 1  # Default to "No"
        self.state = "confirm_delete"
        self.buzzer.beep()

    def confirm_delete_profile(self):
        """Delete the active profile after confirmation."""
        profile_name = self.active_profile()["name"]
        try:
            self.store.delete_profile(profile_name)
            self.status_key = "saved"
            self.buzzer.double_beep()
        except ValueError:
            self.status_key = "error"
            self.buzzer.warning_beep()
        self.state = "live"

    def reset_configuration(self):
        """Reset profiles, calibration, and runtime config to defaults."""
        self.store.save(self.store.default_data())
        save_calibration(config.DEFAULT_TARE_OFFSET, config.DEFAULT_SCALE_FACTOR)
        self.runtime_stable_lock_count = config.STABLE_LOCK_COUNT
        self.runtime_stable_freeze_ms = config.STABLE_FREEZE_MS
        self.locked_weight = None
        self.stable_count = 0
        self.status_key = "saved"
        self.buzzer.double_beep()
        self.state = "live"

    def start_calibration(self):
        """Start the calibration wizard."""
        self.cal_points = []
        self.cal_raw = 0
        self.cal_weight = config.CALIBRATE_DEFAULT_WEIGHT
        self.cal_option = 0
        self.cal_tare_offset = 0
        self.cal_profile_g = self.active_profile()["g"]
        self.state = "cal_tare"
        self.buzzer.beep()

    def _read_cal_raw(self):
        """Read averaged raw sensor value for calibration display."""
        self.cal_raw = self._read_cal_raw_avg()
        return self.cal_raw

    def _read_cal_raw_avg(self):
        """Average calibration raw values via scale API (single averaging layer)."""
        return self.scale.read_raw_avg(config.CALIBRATE_RAW_AVG_COUNT)

    def _save_cal_tare(self):
        """Save tare offset during calibration."""
        self.cal_tare_offset = self._read_cal_raw_avg()
        self.state = "cal_place"
        self.buzzer.beep()

    def _save_cal_point(self):
        """Save current calibration point."""
        raw = self._read_cal_raw_avg()
        self.cal_points.append((raw, self.cal_weight))
        self.cal_option = 0
        self.state = "cal_confirm"
        self.buzzer.beep()

    def _change_cal_weight(self, direction, fast=False):
        """Adjust calibration weight input."""
        if fast:
            step = config.CALIBRATE_WEIGHT_STEP_FAST
        else:
            step = config.CALIBRATE_WEIGHT_STEP
        self.cal_weight += direction * step
        self.cal_weight = max(config.CALIBRATE_WEIGHT_MIN, 
                              min(config.CALIBRATE_WEIGHT_MAX, self.cal_weight))
        self.cal_weight = round(self.cal_weight, 2)

    def _finish_calibration(self):
        """Calculate and apply calibration from collected points."""
        if not self.cal_points:
            self.state = "live"
            return

        # Least-squares slope with tare offset fixed:
        #   raw - tare = scale_factor * base_mass
        sum_mr = 0.0
        sum_mm = 0.0
        for raw, weight in self.cal_points:
            # Convert entered profile-based weight to g=1 base mass.
            # Example on Earth profile (g=9.8): 5.00 shown weight -> 0.5102 base mass.
            base_mass = weight / self.cal_profile_g if self.cal_profile_g else 0
            if base_mass > 0:
                raw_delta = raw - self.cal_tare_offset
                sum_mr += base_mass * raw_delta
                sum_mm += base_mass * base_mass

        if sum_mm <= 0:
            self.state = "live"
            self.buzzer.warning_beep()
            return

        new_scale_factor = sum_mr / sum_mm
        self.scale.scale_factor = new_scale_factor
        self.scale.offset = self.cal_tare_offset
        
        save_calibration(self.cal_tare_offset, new_scale_factor)
        
        self.state = "cal_done"
        self.buzzer.double_beep()

    def _buffer_name(self):
        return "".join(self.name_buffer).strip() or "PROFILE"

    def _change_current_char(self, direction):
        current = self.name_buffer[self.name_position]
        try:
            idx = self.charset.index(current)
        except ValueError:
            idx = 0
        idx = (idx + direction) % len(self.charset)
        self.name_buffer[self.name_position] = self.charset[idx]

    def _change_g(self, direction):
        self.temp_g = clamp_g_value(self.temp_g + (direction * config.G_STEP))

    def _save_name_and_continue(self):
        name = self._buffer_name()
        if self.create_mode:
            try:
                self.store.create_profile(name, self.temp_g)
            except ValueError:
                name = name[: max(1, config.PROFILE_NAME_LENGTH - 1)] + "1"
                self.store.create_profile(name, self.temp_g)
            self.state = "edit_g"
        else:
            self.store.update_profile(self.active_profile()["name"], new_name=name)
            self.state = "live"
            self.buzzer.double_beep()

    def _save_g_and_exit(self):
        name = self.active_profile()["name"]
        if self.create_mode:
            self.store.update_profile(name, g_value=self.temp_g)
            self.create_mode = False
        else:
            self.store.update_profile(name, g_value=self.temp_g)
        self.state = "live"
        self.status_key = "saved"
        self.buzzer.double_beep()

    def send_record(self, dry_run=None):
        profile = self.active_profile()
        payload = build_payload(
            profile_name=profile["name"],
            g_value=profile["g"],
            weight_kg=self.current_weight,
            language=self.language,
        )
        if dry_run is None:
            dry_run = False
        ok, result = self.cloud.send_payload(payload, dry_run=dry_run)
        self.status_key = "upload_ok" if ok else "upload_fail"
        if ok:
            self.buzzer.double_beep()
        else:
            self.buzzer.warning_beep()
        return ok, result

    def handle_events(self, events):
        for event in events:
            if self.state == "live":
                self._handle_live_event(event)
            elif self.state == "menu":
                self._handle_menu_event(event)
            elif self.state == "profile_menu":
                self._handle_profile_menu_event(event)
            elif self.state == "language_menu":
                self._handle_language_menu_event(event)
            elif self.state == "edit_name":
                self._handle_name_event(event)
            elif self.state == "edit_g":
                self._handle_g_event(event)
            elif self.state == "select_profile":
                self._handle_profile_select_event(event)
            elif self.state == "confirm_delete":
                self._handle_delete_event(event)
            elif self.state == "cal_tare":
                self._handle_cal_tare_event(event)
            elif self.state == "cal_place":
                self._handle_cal_place_event(event)
            elif self.state == "cal_input":
                self._handle_cal_input_event(event)
            elif self.state == "cal_confirm":
                self._handle_cal_confirm_event(event)
            elif self.state == "cal_done":
                self._handle_cal_done_event(event)

    def _handle_live_event(self, event):
        if event == "cw":
            self.action_index = (self.action_index - 1) % len(config.DEFAULT_ACTIONS)
            self.buzzer.beep(20)
        elif event == "ccw":
            self.action_index = (self.action_index + 1) % len(config.DEFAULT_ACTIONS)
            self.buzzer.beep(20)
        elif event == "click":
            action = config.DEFAULT_ACTIONS[self.action_index]
            if action == "menu":
                self.state = "menu"
                self.menu_index = 1 if len(self.menu_keys) > 1 else 0
            elif action == "tare":
                self.tare_scale()
            elif action == "profile":
                self.state = "profile_menu"
                self.profile_menu_index = 1 if len(self.profile_menu_keys) > 1 else 0
            elif action == "send":
                self.send_record()

    def _handle_menu_event(self, event):
        if event == "cw":
            self.menu_index = (self.menu_index - 1) % len(self.menu_keys)
            self.buzzer.beep(20)
        elif event == "ccw":
            self.menu_index = (self.menu_index + 1) % len(self.menu_keys)
            self.buzzer.beep(20)
        elif event == "click":
            self.activate_menu()
        elif event == "long":
            self.state = "live"

    def _handle_profile_menu_event(self, event):
        if event == "cw":
            self.profile_menu_index = (self.profile_menu_index - 1) % len(self.profile_menu_keys)
            self.buzzer.beep(20)
        elif event == "ccw":
            self.profile_menu_index = (self.profile_menu_index + 1) % len(self.profile_menu_keys)
            self.buzzer.beep(20)
        elif event == "click":
            self.activate_profile_menu()
        elif event == "long":
            self.state = "live"

    def _handle_language_menu_event(self, event):
        if event == "cw":
            self.language_menu_index = (self.language_menu_index - 1) % len(self.language_menu_keys)
            self.buzzer.beep(20)
        elif event == "ccw":
            self.language_menu_index = (self.language_menu_index + 1) % len(self.language_menu_keys)
            self.buzzer.beep(20)
        elif event == "click":
            self.activate_language_menu()
        elif event == "long":
            self.state = "menu"

    def _handle_name_event(self, event):
        if event == "cw":
            self._change_current_char(-1)
        elif event == "ccw":
            self._change_current_char(1)
        elif event == "click":
            self.name_position = (self.name_position + 1) % config.PROFILE_NAME_LENGTH
        elif event == "long":
            self._save_name_and_continue()
        self.buzzer.beep(20)

    def _handle_g_event(self, event):
        if event == "cw":
            self._change_g(-1)
            self.buzzer.beep(20)
        elif event == "ccw":
            self._change_g(1)
            self.buzzer.beep(20)
        elif event == "click":
            self._save_g_and_exit()
        elif event == "long":
            self.state = "live"

    def _handle_display_calibration_event(self, event):
        if event in ("click", "long"):
            self.state = "menu"

    def _handle_edit_config_event(self, event):
        if event == "cw":
            if self.config_edit_index == 0:
                self.runtime_stable_lock_count = max(1, self.runtime_stable_lock_count - 1)
            else:
                self.runtime_stable_freeze_ms = max(1000, self.runtime_stable_freeze_ms - 500)
            self.buzzer.beep(20)
        elif event == "ccw":
            if self.config_edit_index == 0:
                self.runtime_stable_lock_count = min(20, self.runtime_stable_lock_count + 1)
            else:
                self.runtime_stable_freeze_ms = min(20000, self.runtime_stable_freeze_ms + 500)
            self.buzzer.beep(20)
        elif event == "click":
            self.config_edit_index = (self.config_edit_index + 1) % 2
            self.buzzer.beep(20)
        elif event == "long":
            self.status_key = "saved"
            self.state = "menu"

    def _handle_profile_select_event(self, event):
        total_items = len(self.profile_menu_items)
        if total_items == 0:
            self.state = "live"
            return
        if event == "cw":
            self.profile_list_index = (self.profile_list_index - 1) % total_items
            self.buzzer.beep(20)
        elif event == "ccw":
            self.profile_list_index = (self.profile_list_index + 1) % total_items
            self.buzzer.beep(20)
        elif event == "click":
            self.select_profile_at_index()
        elif event == "long":
            self.state = "profile_menu"

    def _handle_delete_event(self, event):
        if event == "cw" or event == "ccw":
            self.delete_option = 1 - self.delete_option
            self.buzzer.beep(20)
        elif event == "click":
            if self.delete_option == 0:  # Yes
                self.confirm_delete_profile()
            else:  # No
                self.state = "live"
        elif event == "long":
            self.state = "live"

    def _handle_cal_tare_event(self, event):
        if event == "click":
            self._save_cal_tare()
        elif event == "long":
            self.state = "live"

    def _handle_cal_place_event(self, event):
        if event == "click":
            self.state = "cal_input"
            self.buzzer.beep()
        elif event == "long":
            self.state = "live"

    def _get_ms(self):
        """Get current time in milliseconds."""
        try:
            return time.ticks_ms()
        except AttributeError:
            return int(time.time() * 1000)

    def _handle_cal_input_event(self, event):
        if event == "cw" or event == "ccw":
            now = self._get_ms()
            try:
                elapsed = time.ticks_diff(now, self.cal_last_rotate)
            except AttributeError:
                elapsed = now - self.cal_last_rotate
            fast = elapsed < config.CALIBRATE_FAST_THRESHOLD_MS
            self.cal_last_rotate = now
            
            direction = -1 if event == "cw" else 1
            self._change_cal_weight(direction, fast=fast)
            self.buzzer.beep(20)
        elif event == "click":
            self._save_cal_point()
        elif event == "long":
            self.state = "live"

    def _handle_cal_confirm_event(self, event):
        if event == "cw" or event == "ccw":
            self.cal_option = 1 - self.cal_option
            self.buzzer.beep(20)
        elif event == "click":
            if self.cal_option == 0:
                self.state = "cal_place"
                self.cal_weight = config.CALIBRATE_DEFAULT_WEIGHT
            else:
                self._finish_calibration()
        elif event == "long":
            self.state = "live"

    def _handle_cal_done_event(self, event):
        if event in ("click", "long"):
            self.state = "live"

    def render(self):
        profile = self.active_profile()
        language = self.language
        if self.state == "live":
            self.refresh_weight()
            # Use locked_weight if frozen, otherwise current_weight
            display_weight = self.locked_weight if self.locked_weight is not None else self.current_weight
            self.ui.draw_live(
                language,
                display_weight,
                profile["name"],
                profile["g"],
                self.status_key,  # Use status_key which includes "locked" state
                tr(language, self.status_key),
                self.action_index,
            )
        elif self.state == "menu":
            items = [tr(language, key) for key in self.menu_keys]
            self.ui.draw_menu(language, items, self.menu_index)
        elif self.state == "profile_menu":
            items = [tr(language, key) for key in self.profile_menu_keys]
            self.ui.draw_menu(language, items, self.profile_menu_index, title_key="profiles")
        elif self.state == "language_menu":
            items = [tr(language, key) for key in self.language_menu_keys]
            self.ui.draw_menu(language, items, self.language_menu_index, title_key="language")
        elif self.state == "edit_name":
            self.ui.draw_message(
                language,
                tr(language, "edit_name"),
                self._buffer_name(),
                "Long Save Next",
            )
        elif self.state == "edit_g":
            self.ui.draw_message(
                language,
                tr(language, "edit_g"),
                "%.1f m/s2" % self.temp_g,
                "Click Save",
            )
        elif self.state == "select_profile":
            self.ui.draw_profile_list(language, self.profile_menu_items, self.profile_list_index)
        elif self.state == "confirm_delete":
            self.ui.draw_confirm_delete(
                language,
                profile["name"],
                self.delete_option,
            )
        elif self.state == "cal_tare":
            self._read_cal_raw()
            self.ui.draw_calibrate_tare(language, self.cal_raw)
        elif self.state == "cal_place":
            self._read_cal_raw()
            self.ui.draw_calibrate_place(language, self.cal_raw, len(self.cal_points) + 1)
        elif self.state == "cal_input":
            self.ui.draw_calibrate_input(language, self.cal_weight, len(self.cal_points) + 1)
        elif self.state == "cal_confirm":
            self.ui.draw_calibrate_confirm(language, self.cal_option, len(self.cal_points))
        elif self.state == "cal_done":
            self.ui.draw_calibrate_done(language, self.scale.scale_factor)

    def auto_tare_on_startup(self):
        """Wait for stable reading and auto-tare on startup."""
        self.ui.draw_message(
            self.language,
            tr(self.language, "tare"),
            "Auto-tare...",
            "Keep scale empty",
        )
        
        # Fill history with readings first (keep input responsive).
        for _ in range(config.STABLE_WINDOW + 2):
            pending = self.encoder.poll()
            if pending:
                self.handle_events(pending)
            self.scale.read_filtered_kg()
            time.sleep(config.MAIN_LOOP_DELAY_MS / 1000.0)
        
        # Wait for stability
        wait_interval = 100  # ms
        max_iterations = config.AUTO_TARE_TIMEOUT_MS // wait_interval
        for _ in range(max_iterations):
            pending = self.encoder.poll()
            if pending:
                self.handle_events(pending)
            self.scale.read_filtered_kg()
            if self.scale.stability_level() == "stable":
                break
            time.sleep(wait_interval / 1000.0)
        
        # Tare the scale and save to persistent storage
        self.scale.tare()
        save_calibration(self.scale.offset, self.scale.scale_factor)
        self.buzzer.double_beep()

    def run(self, iterations=None):
        self.ui.splash(self.language)
        time.sleep(config.SPLASH_MS / 1000.0)
        self.auto_tare_on_startup()
        count = 0
        last_render_ms = 0
        while True:
            # High-priority input servicing: drain interrupt queue before rendering.
            had_events = False
            pending = self.encoder.poll()
            while pending:
                had_events = True
                self.handle_events(pending)
                pending = self.encoder.poll()
            now = self._get_time_ms()
            try:
                elapsed_since_render = time.ticks_diff(now, last_render_ms)
            except AttributeError:
                elapsed_since_render = now - last_render_ms

            # Redraw only on user input or periodic UI refresh.
            if had_events or elapsed_since_render >= config.UI_REDRAW_MS:
                self.render()
                last_render_ms = now

            # If new events arrived, loop immediately; otherwise short sleep.
            if not self.encoder.has_pending_events():
                time.sleep(config.MAIN_LOOP_DELAY_MS / 1000.0)
            count += 1
            if iterations is not None and count >= iterations:
                break


def build_app():
    store = ProfileStore(config.PROFILE_FILE)
    if HX711 is None:
        raise RuntimeError("Hardware build requires MicroPython on the Pico")
    adc = HX711(config.HX711_DATA_PIN, config.HX711_SCK_PIN, gain=config.HX711_GAIN)
    cal_offset, cal_scale = load_calibration()
    scale = ScaleSensor(adc, offset=cal_offset, scale_factor=cal_scale)
    display = create_default_display(config)
    encoder = RotaryEncoder(config.ENCODER_CLK_PIN, config.ENCODER_DT_PIN, config.ENCODER_SW_PIN)
    cloud = CloudClient()
    ui = DisplayUI(display)
    buzzer = Buzzer(config.BUZZER_PIN)
    return WeighingMachineApp(store, scale, ui, encoder, buzzer, cloud)


def main():
    build_app().run()


if __name__ == "__main__":
    main()
