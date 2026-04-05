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
from modules.scale import ScaleSensor

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
            "select_profile",
            "create_profile",
            "edit_name",
            "edit_g",
            "language",
            "buzzer_test",
        ]
        self.menu_index = 0
        self.action_index = 0
        self.status_key = "stable"
        self.current_weight = 0.0
        self.name_buffer = list("PROFILE   ")
        self.name_position = 0
        self.temp_g = config.DEFAULT_G_VALUE
        self.create_mode = False
        self.charset = config.PROFILE_NAME_CHARSET

    @property
    def language(self):
        return self.store.get_language()

    def active_profile(self):
        return self.store.get_active_profile()

    def refresh_weight(self):
        self.current_weight = self.scale.read_kg()
        self.status_key = "stable" if self.scale.is_stable() else "not_ready"
        return self.current_weight

    def tare_scale(self):
        self.scale.tare()
        self.status_key = "saved"
        self.buzzer.double_beep()

    def cycle_profile(self):
        profiles = self.store.list_profiles()
        current = self.active_profile()["name"]
        names = [item["name"] for item in profiles]
        idx = (names.index(current) + 1) % len(names)
        self.store.select_profile(names[idx])
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
        current = self.active_profile()["name"].ljust(config.PROFILE_NAME_LENGTH)
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
        if key == "select_profile":
            self.cycle_profile()
            self.state = "live"
        elif key == "create_profile":
            self.start_create_profile()
        elif key == "edit_name":
            self.start_edit_name()
        elif key == "edit_g":
            self.start_edit_g()
        elif key == "language":
            self.toggle_language()
            self.state = "live"
        elif key == "buzzer_test":
            self.buzzer.warning_beep()
            self.state = "live"

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
            elif self.state == "edit_name":
                self._handle_name_event(event)
            elif self.state == "edit_g":
                self._handle_g_event(event)

    def _handle_live_event(self, event):
        if event == "cw":
            self.action_index = (self.action_index + 1) % len(config.DEFAULT_ACTIONS)
            self.buzzer.beep(20)
        elif event == "ccw":
            self.action_index = (self.action_index - 1) % len(config.DEFAULT_ACTIONS)
            self.buzzer.beep(20)
        elif event == "click":
            action = config.DEFAULT_ACTIONS[self.action_index]
            if action == "menu":
                self.state = "menu"
            elif action == "tare":
                self.tare_scale()
            elif action == "profile":
                self.cycle_profile()
            elif action == "send":
                self.send_record()
        elif event == "long":
            self.state = "menu"

    def _handle_menu_event(self, event):
        if event == "cw":
            self.menu_index = (self.menu_index + 1) % len(self.menu_keys)
            self.buzzer.beep(20)
        elif event == "ccw":
            self.menu_index = (self.menu_index - 1) % len(self.menu_keys)
            self.buzzer.beep(20)
        elif event == "click":
            self.activate_menu()
        elif event == "long":
            self.state = "live"

    def _handle_name_event(self, event):
        if event == "cw":
            self._change_current_char(1)
        elif event == "ccw":
            self._change_current_char(-1)
        elif event == "click":
            self.name_position = (self.name_position + 1) % config.PROFILE_NAME_LENGTH
        elif event == "long":
            self._save_name_and_continue()
        self.buzzer.beep(20)

    def _handle_g_event(self, event):
        if event == "cw":
            self._change_g(1)
            self.buzzer.beep(20)
        elif event == "ccw":
            self._change_g(-1)
            self.buzzer.beep(20)
        elif event == "click":
            self._save_g_and_exit()
        elif event == "long":
            self.state = "live"

    def render(self):
        profile = self.active_profile()
        language = self.language
        if self.state == "live":
            self.refresh_weight()
            self.ui.draw_live(
                language,
                self.current_weight,
                profile["name"],
                profile["g"],
                self.scale.is_stable(),
                tr(language, self.status_key),
                self.action_index,
            )
        elif self.state == "menu":
            items = [tr(language, key) for key in self.menu_keys]
            self.ui.draw_menu(language, items, self.menu_index)
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

    def run(self, iterations=None):
        self.ui.splash(self.language)
        time.sleep(config.SPLASH_MS / 1000.0)
        count = 0
        while True:
            self.handle_events(self.encoder.poll())
            self.render()
            time.sleep(config.MAIN_LOOP_DELAY_MS / 1000.0)
            count += 1
            if iterations is not None and count >= iterations:
                break


def build_app():
    store = ProfileStore(config.PROFILE_FILE)
    if HX711 is None:
        raise RuntimeError("Hardware build requires MicroPython on the Pico")
    adc = HX711(config.HX711_DATA_PIN, config.HX711_SCK_PIN, gain=config.HX711_GAIN)
    scale = ScaleSensor(adc, scale_factor=config.DEFAULT_SCALE_FACTOR)
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
