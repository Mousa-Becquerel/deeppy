"""
Test scaffolding — sets up a per-session temp SQLite DB and a FastAPI TestClient.

Critical: env vars are written BEFORE the api module is imported, so the engine
+ config are built against the test DB and a deterministic JWT secret.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

# --- 1. Force a clean, isolated environment BEFORE any app imports ---------

_TMP_DIR = Path(tempfile.mkdtemp(prefix="dpp_test_"))
_DB_FILE = _TMP_DIR / "test.db"
_UPLOADS = _TMP_DIR / "uploads"
_UPLOADS.mkdir(exist_ok=True)
_DATA = _TMP_DIR / "data"
_DATA.mkdir(exist_ok=True)

os.environ["DATABASE_URL"] = f"sqlite:///{_DB_FILE.as_posix()}"
os.environ["DATA_DIR"] = str(_DATA)
os.environ["UPLOADS_DIR"] = str(_UPLOADS)
os.environ["JWT_SECRET"] = "test-secret-only-for-pytest-do-not-use-anywhere-else"
os.environ["ENVIRONMENT"] = "development"
# Disable provider keys so the app doesn't try to reach Gemini/OpenAI.
os.environ.setdefault("GOOGLE_API_KEY", "")
os.environ.setdefault("OPENAI_API_KEY", "")

# Now safe to import the app.
from fastapi.testclient import TestClient  # noqa: E402

import api as api_module  # noqa: E402


# --- 2. Per-test fresh state -----------------------------------------------

@pytest.fixture(autouse=True)
def _reset_in_memory_state():
    """Clear the in-memory _jobs dict between tests."""
    api_module._jobs.clear()
    yield


@pytest.fixture
def client() -> TestClient:
    """An unauthenticated TestClient. Use the `register`/`login` helpers below
    to obtain a cookie-bearing client."""
    return TestClient(api_module.app)


# --- 3. Helpers shared by every test ---------------------------------------

# Module-level counter — emails MUST be unique across the whole session because
# the DB is only reset at session start, not per-test.
_email_counter = {"n": 0}


@pytest.fixture
def register():
    """Register a user and return their cookie-bearing TestClient."""

    def _register(client: TestClient, email: str | None = None,
                  password: str = "supersecretpass1", company: str = "Test Co",
                  name: str = "Test User") -> tuple[TestClient, dict]:
        _email_counter["n"] += 1
        email = email or f"user{_email_counter['n']}@test.local"
        r = client.post("/api/auth/register", json={
            "company_name": company, "email": email,
            "password": password, "name": name,
        })
        assert r.status_code == 200, r.text
        return client, r.json()["user"]

    return _register


@pytest.fixture
def auth_client(client, register):
    """A TestClient already logged in as a freshly-registered admin user.
    Returns (client, user_dict). The cookie persists on the client."""
    return register(client)


# --- 4. Reset the DB before each test session ------------------------------

@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    """Drop and recreate all tables once per pytest session."""
    from dpp_extractor.db.database import Base, engine
    from dpp_extractor.db import models  # noqa: F401 — register models
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
