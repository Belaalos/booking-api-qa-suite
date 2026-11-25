import pytest
import requests
from jsonschema import validate

from conftest import BASE_URL

JSON = {"Accept": "application/json"}

BOOKING_SCHEMA = {
    "type": "object",
    "required": ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
    "properties": {
        "firstname": {"type": "string"},
        "lastname": {"type": "string"},
        "totalprice": {"type": "integer"},
        "depositpaid": {"type": "boolean"},
        "bookingdates": {
            "type": "object",
            "required": ["checkin", "checkout"],
            "properties": {"checkin": {"type": "string"}, "checkout": {"type": "string"}},
        },
        "additionalneeds": {"type": "string"},
    },
}


def test_health_check():
    resp = requests.get(f"{BASE_URL}/ping", timeout=15)
    assert resp.status_code == 201


def test_create_booking_returns_id_and_echoes_data(booking_payload):
    resp = requests.post(f"{BASE_URL}/booking", json=booking_payload, headers=JSON, timeout=15)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["bookingid"], int)
    assert body["booking"]["firstname"] == "Belal"
    assert body["booking"]["bookingdates"] == booking_payload["bookingdates"]


def test_get_booking_matches_schema(created_booking):
    resp = requests.get(f"{BASE_URL}/booking/{created_booking}", headers=JSON, timeout=15)
    assert resp.status_code == 200
    validate(resp.json(), BOOKING_SCHEMA)


def test_created_booking_appears_in_list(created_booking):
    resp = requests.get(f"{BASE_URL}/booking", timeout=15)
    assert resp.status_code == 200
    assert created_booking in [b["bookingid"] for b in resp.json()]


def test_filter_by_name(created_booking):
    resp = requests.get(f"{BASE_URL}/booking", params={"firstname": "Belal", "lastname": "Tester"}, timeout=15)
    assert resp.status_code == 200
    assert created_booking in [b["bookingid"] for b in resp.json()]


def test_full_update_with_token(created_booking, booking_payload, token):
    booking_payload["firstname"] = "Updated"
    booking_payload["totalprice"] = 999
    resp = requests.put(
        f"{BASE_URL}/booking/{created_booking}",
        json=booking_payload,
        headers={**JSON, "Cookie": f"token={token}"},
        timeout=15,
    )
    assert resp.status_code == 200
    assert resp.json()["firstname"] == "Updated"
    after = requests.get(f"{BASE_URL}/booking/{created_booking}", headers=JSON, timeout=15).json()
    assert after["totalprice"] == 999


def test_partial_update_changes_only_sent_fields(created_booking, token):
    resp = requests.patch(
        f"{BASE_URL}/booking/{created_booking}",
        json={"lastname": "Patched"},
        headers={**JSON, "Cookie": f"token={token}"},
        timeout=15,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["lastname"] == "Patched"
    assert body["firstname"] == "Belal"


def test_delete_then_get_returns_404(created_booking, token):
    resp = requests.delete(f"{BASE_URL}/booking/{created_booking}", headers={"Cookie": f"token={token}"}, timeout=15)
    assert resp.status_code == 201
    assert requests.get(f"{BASE_URL}/booking/{created_booking}", timeout=15).status_code == 404
