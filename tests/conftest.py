import pytest
import requests

BASE_URL = "https://restful-booker.herokuapp.com"

BOOKING = {
    "firstname": "Belal",
    "lastname": "Tester",
    "totalprice": 150,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-05"},
    "additionalneeds": "Breakfast",
}


@pytest.fixture(scope="session")
def token():
    resp = requests.post(
        f"{BASE_URL}/auth",
        json={"username": "admin", "password": "password123"},
        timeout=15,
    )
    assert resp.status_code == 200
    return resp.json()["token"]


@pytest.fixture
def booking_payload():
    return dict(BOOKING, bookingdates=dict(BOOKING["bookingdates"]))


@pytest.fixture
def created_booking(booking_payload):
    """Creates a booking for the test and removes it afterwards."""
    resp = requests.post(
        f"{BASE_URL}/booking",
        json=booking_payload,
        headers={"Accept": "application/json"},
        timeout=15,
    )
    assert resp.status_code == 200
    booking_id = resp.json()["bookingid"]
    yield booking_id
    # cleanup is best effort, the shared server sometimes resets itself
    auth = requests.post(f"{BASE_URL}/auth", json={"username": "admin", "password": "password123"}, timeout=15)
    requests.delete(f"{BASE_URL}/booking/{booking_id}", headers={"Cookie": f"token={auth.json()['token']}"}, timeout=15)
