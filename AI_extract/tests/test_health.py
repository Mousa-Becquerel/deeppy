"""H4 — /api/health is unauth, returns 200, reports environment."""


def test_health_is_public(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "environment" in body


def test_health_does_not_require_auth(client):
    # No cookie set at all.
    client.cookies.clear()
    assert client.get("/api/health").status_code == 200
