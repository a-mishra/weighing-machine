import os
import sys

sys.path.insert(0, os.getcwd())

from modules.cloud import CloudClient, build_payload


class FakeWLAN:
    def __init__(self):
        self.connected = False

    def active(self, enabled):
        self.enabled = enabled

    def isconnected(self):
        return self.connected

    def connect(self, ssid, password):
        self.connected = True


class FakeResponse:
    status_code = 200

    def json(self):
        return {"ok": True}

    def close(self):
        return None


class FakeRequests:
    def post(self, endpoint, json=None):
        assert endpoint.startswith("http")
        assert "weight_kg" in json
        return FakeResponse()


def main():
    payload = build_payload("default", 9.8, 1.25, "en")
    assert payload["profile_name"] == "default"
    assert payload["weight_kg"] == 1.25

    dry_client = CloudClient(endpoint="http://example.com/api/weights")
    ok, result = dry_client.send_payload(payload, dry_run=True)
    assert ok is True
    assert result["dry_run"] is True

    realish_client = CloudClient(
        endpoint="http://example.com/api/weights",
        wlan=FakeWLAN(),
        request_module=FakeRequests(),
    )
    ok, result = realish_client.send_payload(payload)
    assert ok is True
    assert result["status_code"] == 200
    print("test_cloud.py OK", result)


if __name__ == "__main__":
    main()
