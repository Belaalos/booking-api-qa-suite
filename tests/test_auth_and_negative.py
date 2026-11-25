import pytest
import requests

from conftest import BASE_URL

JSON = {"Accept": "application/json"}


def test_auth_returns_token(token):
    assert isinstance(token, str) and len(token) > 5


def test_auth_with_wrong_password():
    resp = requests.post(f"{BASE_URL}/auth", json={"username": "admin", "password": "wrong"}, timeout=15)
    # this API answers 200 with a reason instead of 401
    assert resp.status_code == 200
    assert resp.json() == {"reason": "Bad credentials"}


def test_update_without_token_is_forbidden(created_booking, booking_payload):
    resp = requests.put(f"{BASE_URL}/booking/{created_booking}", json=booking_payload, headers=JSON, timeout=15)
    assert resp.status_code == 403


def test_delete_without_token_is_forbidden(created_booking):
    resp = requests.delete(f"{BASE_URL}/booking/{created_booking}", timeout=15)
    assert resp.status_code == 403


def test_update_with_invalid_token_is_forbidden(created_booking, booking_payload):
    resp = requests.put(
        f"{BASE_URL}/booking/{created_booking}",
        json=booking_payload,
        headers={**JSON, "Cookie": "token=notarealtoken"},
        timeout=15,
    )
    assert resp.status_code == 403


def test_get_unknown_booking_is_404():
    assert requests.get(f"{BASE_URL}/booking/99999999", timeout=15).status_code == 404


def test_create_with_missing_fields_is_rejected():
    resp = requests.post(f"{BASE_URL}/booking", json={"firstname": "Only"}, headers=JSON, timeout=15)
    assert resp.status_code >= 400
