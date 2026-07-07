"""Regression: empty-string JWT_SECRET must fall back to the dev default.

Failing this test means docker-compose's `${JWT_SECRET:-}` expansion (or any
unset-on-host scenario) will produce an empty HMAC key at runtime and crash
every login with InvalidKeyError.
"""
import importlib
import os


def test_empty_jwt_secret_env_falls_back_to_dev_default(monkeypatch):
    # Force JWT_SECRET to empty string and reimport config.
    monkeypatch.setenv("JWT_SECRET", "")
    from dpp_extractor import config as cfg
    importlib.reload(cfg)
    assert cfg.JWT_SECRET == cfg.JWT_SECRET_DEV_DEFAULT
    assert cfg.JWT_SECRET  # truthy, non-empty


def test_unset_jwt_secret_env_uses_dev_default(monkeypatch):
    monkeypatch.delenv("JWT_SECRET", raising=False)
    from dpp_extractor import config as cfg
    importlib.reload(cfg)
    assert cfg.JWT_SECRET == cfg.JWT_SECRET_DEV_DEFAULT


def test_explicit_jwt_secret_env_wins(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "a-real-secret-of-sufficient-length-1234")
    from dpp_extractor import config as cfg
    importlib.reload(cfg)
    assert cfg.JWT_SECRET == "a-real-secret-of-sufficient-length-1234"


def test_restore_test_secret(monkeypatch):
    """Cleanup: restore the conftest's test secret so subsequent tests work."""
    monkeypatch.setenv("JWT_SECRET", "test-secret-only-for-pytest-do-not-use-anywhere-else")
    from dpp_extractor import config as cfg
    importlib.reload(cfg)
    assert cfg.JWT_SECRET.startswith("test-secret-only")
