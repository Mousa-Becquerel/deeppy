"""Auth happy + sad paths."""

def test_register_creates_company_and_admin(client, register):
    _, user = register(client, email="founder@example.com")
    assert user["email"] == "founder@example.com"
    assert user["role"] == "admin"
    assert user["company_id"]
    # Cookie was set
    assert "deeppy_session" in client.cookies


def test_me_works_with_cookie(client, register):
    register(client, email="me@example.com")
    r = client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["user"]["email"] == "me@example.com"


def test_me_unauthenticated_is_401(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_login_wrong_password_is_401(client, register):
    register(client, email="alice@example.com", password="originalpass1")
    # Clear cookie
    client.cookies.clear()
    r = client.post("/api/auth/login", json={
        "email": "alice@example.com", "password": "wrongpass1"
    })
    assert r.status_code == 401


def test_register_duplicate_email_is_409(client, register):
    register(client, email="dup@example.com")
    client.cookies.clear()
    r = client.post("/api/auth/register", json={
        "company_name": "Other Co", "email": "dup@example.com",
        "password": "anotherpass1", "name": "Other",
    })
    assert r.status_code == 409


def test_register_weak_password_is_400(client):
    r = client.post("/api/auth/register", json={
        "company_name": "X", "email": "weak@example.com",
        "password": "short", "name": "X",
    })
    assert r.status_code == 400


def test_logout_clears_session(client, register):
    register(client, email="logout@example.com")
    assert client.get("/api/auth/me").status_code == 200
    r = client.post("/api/auth/logout")
    assert r.status_code == 200
    # Cookie should be cleared
    assert client.get("/api/auth/me").status_code == 401


def test_inactive_user_cannot_authenticate(client, register):
    """Marking a user inactive in the DB should immediately revoke access."""
    client_, user = register(client, email="dormant@example.com")
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import models
    with session_scope() as db:
        db.get(models.User, user["id"]).is_active = False
    assert client_.get("/api/auth/me").status_code == 401
