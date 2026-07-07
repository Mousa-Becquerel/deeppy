"""H1 — /api/auth/login is rate-limited per (IP, email)."""

import pytest

from dpp_extractor.rate_limit import login_limiter


@pytest.fixture(autouse=True)
def _reset_limiter():
    """Each test starts with empty buckets so the 5/min budget is fresh."""
    login_limiter.reset()
    yield
    login_limiter.reset()


def test_six_wrong_logins_in_a_row_get_429(client, register):
    register(client, email="bruteme@example.com", password="goodpass1")
    client.cookies.clear()

    for _ in range(5):
        r = client.post("/api/auth/login", json={
            "email": "bruteme@example.com", "password": "wrong"
        })
        assert r.status_code == 401  # wrong password, but still allowed
    # 6th attempt hits the limiter.
    r = client.post("/api/auth/login", json={
        "email": "bruteme@example.com", "password": "wrong"
    })
    assert r.status_code == 429
    assert "Retry-After" in r.headers


def test_limit_is_per_email_not_global(client, register):
    """Brute-forcing one account does NOT block a different account."""
    register(client, email="victim_a@example.com", password="rightpass1")
    register(client, email="victim_b@example.com", password="rightpass1")
    client.cookies.clear()

    for _ in range(5):
        client.post("/api/auth/login", json={
            "email": "victim_a@example.com", "password": "wrong"
        })
    # victim_a is now blocked
    assert client.post("/api/auth/login", json={
        "email": "victim_a@example.com", "password": "wrong"
    }).status_code == 429
    # victim_b is NOT blocked
    r = client.post("/api/auth/login", json={
        "email": "victim_b@example.com", "password": "rightpass1"
    })
    assert r.status_code == 200
