"""SIGNUP_ALLOWLIST — private-beta gate on /api/auth/register.

When empty (default in tests), registration is open.
When populated, only listed emails may register; others get 403.
"""
import importlib

import pytest


def _reload_with_env(monkeypatch, allowlist_value: str | None):
    """Reload the config module with a specific SIGNUP_ALLOWLIST value.

    Passing None clears the env var (open registration); passing a string
    sets it verbatim. Also reloads api so its import-time reference to
    SIGNUP_ALLOWLIST picks up the reload.
    """
    if allowlist_value is None:
        monkeypatch.delenv("SIGNUP_ALLOWLIST", raising=False)
    else:
        monkeypatch.setenv("SIGNUP_ALLOWLIST", allowlist_value)
    from dpp_extractor import config as cfg
    importlib.reload(cfg)
    import api as api_mod
    importlib.reload(api_mod)
    return api_mod


def test_empty_allowlist_leaves_registration_open(monkeypatch):
    api_mod = _reload_with_env(monkeypatch, None)
    from dpp_extractor import config
    assert config.SIGNUP_ALLOWLIST == set()

    from fastapi.testclient import TestClient
    client = TestClient(api_mod.app)
    r = client.post("/api/auth/register", json={
        "company_name": "OpenCo", "email": "anyone@public.example",
        "password": "supersecretpass1", "name": "Anyone",
    })
    assert r.status_code == 200, r.text


def test_allowlist_blocks_non_listed_email(monkeypatch):
    api_mod = _reload_with_env(
        monkeypatch, "alice@allowed.example, bob@allowed.example",
    )
    from dpp_extractor import config
    assert config.SIGNUP_ALLOWLIST == {
        "alice@allowed.example", "bob@allowed.example",
    }

    from fastapi.testclient import TestClient
    client = TestClient(api_mod.app)
    r = client.post("/api/auth/register", json={
        "company_name": "SneakyCo", "email": "eve@notallowed.example",
        "password": "supersecretpass1", "name": "Eve",
    })
    assert r.status_code == 403
    assert "invite-only" in r.json().get("detail", "").lower()


def test_allowlist_permits_listed_email(monkeypatch):
    api_mod = _reload_with_env(
        monkeypatch, "alice.list@allowed.example,bob.list@allowed.example",
    )
    from fastapi.testclient import TestClient
    client = TestClient(api_mod.app)
    r = client.post("/api/auth/register", json={
        "company_name": "AliceCo", "email": "alice.list@allowed.example",
        "password": "supersecretpass1", "name": "Alice",
    })
    assert r.status_code == 200, r.text


def test_allowlist_is_case_insensitive_and_whitespace_tolerant(monkeypatch):
    api_mod = _reload_with_env(
        monkeypatch, "   CAROL@Mixed.Example  ,  dave@lower.example  ",
    )
    from fastapi.testclient import TestClient
    client = TestClient(api_mod.app)
    # Same email, different case — should be allowed.
    r = client.post("/api/auth/register", json={
        "company_name": "CarolCo", "email": "carol@mixed.example",
        "password": "supersecretpass1", "name": "Carol",
    })
    assert r.status_code == 200, r.text


def test_reload_reset_for_other_tests(monkeypatch):
    """Housekeeping — ensure downstream tests see an open allowlist again.

    Later tests import api_module directly; if we leave a restrictive
    allowlist behind, they'd hit the gate. Explicitly restore open state.
    """
    _reload_with_env(monkeypatch, None)
    from dpp_extractor import config
    assert config.SIGNUP_ALLOWLIST == set()
