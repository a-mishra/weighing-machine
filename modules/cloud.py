"""Wi-Fi and HTTP upload helper."""

import time

from config import CLOUD_ENDPOINT, CLOUD_TIMEOUT_SECONDS, WIFI_PASSWORD, WIFI_SSID

try:
    import network  # type: ignore
except ImportError:  # pragma: no cover
    network = None

try:
    import urequests as requests  # type: ignore
except ImportError:  # pragma: no cover
    requests = None


def build_payload(profile_name, g_value, weight_kg, language, raw_value=None):
    return {
        "profile_name": profile_name,
        "g_value": float(g_value),
        "weight_kg": float(weight_kg),
        "language": language,
        "raw_value": raw_value,
        "timestamp_ms": int(time.time() * 1000),
    }


class CloudClient:
    def __init__(
        self,
        ssid=WIFI_SSID,
        password=WIFI_PASSWORD,
        endpoint=CLOUD_ENDPOINT,
        timeout=CLOUD_TIMEOUT_SECONDS,
        wlan=None,
        request_module=None,
    ):
        self.ssid = ssid
        self.password = password
        self.endpoint = endpoint
        self.timeout = timeout
        self.wlan = wlan
        self.requests = request_module or requests

    def _default_wlan(self):
        if network is None:
            return None
        return network.WLAN(network.STA_IF)

    def connect_wifi(self):
        wlan = self.wlan or self._default_wlan()
        if wlan is None:
            return False, "no-network-module"
        self.wlan = wlan
        if hasattr(wlan, "active"):
            wlan.active(True)
        if hasattr(wlan, "isconnected") and wlan.isconnected():
            return True, "already-connected"
        if hasattr(wlan, "connect"):
            wlan.connect(self.ssid, self.password)
        for _ in range(self.timeout * 2):
            if hasattr(wlan, "isconnected") and wlan.isconnected():
                return True, "connected"
            time.sleep(0.5)
        return False, "timeout"

    def send_payload(self, payload, dry_run=False):
        if dry_run:
            return True, {"dry_run": True, "endpoint": self.endpoint, "payload": payload}

        ok, status = self.connect_wifi()
        if not ok:
            return False, {"stage": "wifi", "status": status}

        if self.requests is None:
            return False, {"stage": "http", "status": "no-requests-module"}

        response = None
        try:
            response = self.requests.post(self.endpoint, json=payload)
            body = None
            if hasattr(response, "json"):
                try:
                    body = response.json()
                except Exception:
                    body = None
            return True, {"stage": "http", "status_code": getattr(response, "status_code", 200), "body": body}
        except Exception as exc:
            return False, {"stage": "http", "status": str(exc)}
        finally:
            if response and hasattr(response, "close"):
                response.close()
