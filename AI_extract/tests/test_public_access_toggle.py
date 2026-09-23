"""Owners can toggle public access on their own products.

Sept 23: the public_access flag shipped as script-only — changing which
products were publicly readable meant SSH + docker exec, so every change was
a ticket for us. These cover the PATCH path that backs the in-app toggle.

The important guard: a draft must never become publicly readable, or anyone
holding the link could open unpublished work.
"""
from fastapi.testclient import TestClient
import api as api_module


def _seed(company_id: str, *, name: str, status: str = "published") -> str:
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    with session_scope() as db:
        p = repo.create_product(
            db, passport={}, completeness=0.0, source_documents=[],
            company_id=company_id, status=status,
        )
        repo.update_product_fields(db, p.id, name=name)
        return p.id


def test_detail_exposes_public_access(auth_client):
    """The owner's UI needs to read the current state to render the toggle."""
    client, user = auth_client
    pid = _seed(user["company_id"], name="Readable Flag")

    body = client.get(f"/api/products/{pid}").json()
    assert body["public_access"] is False


def test_owner_can_grant_and_revoke(auth_client):
    client, user = auth_client
    pid = _seed(user["company_id"], name="Toggle Me")

    r = client.patch(f"/api/products/{pid}", json={"public_access": True})
    assert r.status_code == 200, r.text
    assert r.json()["public_access"] is True
    assert TestClient(api_module.app).get(f"/api/catalog/public/{pid}").status_code == 200

    r = client.patch(f"/api/products/{pid}", json={"public_access": False})
    assert r.status_code == 200
    assert r.json()["public_access"] is False
    assert TestClient(api_module.app).get(f"/api/catalog/public/{pid}").status_code == 403


def test_cannot_make_a_draft_public(auth_client):
    """Unpublished work must not be openable by link."""
    client, user = auth_client
    pid = _seed(user["company_id"], name="Still A Draft", status="draft")

    r = client.patch(f"/api/products/{pid}", json={"public_access": True})
    assert r.status_code == 400, r.text
    assert client.get(f"/api/products/{pid}").json()["public_access"] is False


def test_publish_and_grant_in_one_request(auth_client):
    """status and public_access in the same PATCH should be accepted."""
    client, user = auth_client
    pid = _seed(user["company_id"], name="Publish And Open", status="draft")

    r = client.patch(f"/api/products/{pid}", json={
        "status": "published", "public_access": True,
    })
    assert r.status_code == 200, r.text
    assert r.json()["public_access"] is True


def test_unpublishing_closes_public_access(auth_client):
    """Even with the flag still set, a non-published product must not resolve
    publicly — the read path gates on status independently."""
    client, user = auth_client
    pid = _seed(user["company_id"], name="Pull It Back")
    client.patch(f"/api/products/{pid}", json={"public_access": True})
    assert TestClient(api_module.app).get(f"/api/catalog/public/{pid}").status_code == 200

    client.patch(f"/api/products/{pid}", json={"status": "draft"})
    assert TestClient(api_module.app).get(f"/api/catalog/public/{pid}").status_code == 404


def test_other_company_cannot_toggle(register):
    """Tenant scoping still applies to the new field."""
    a = TestClient(api_module.app)
    _, ua = register(a, email="pa_owner@co.example", company="Owner Co")
    b = TestClient(api_module.app)
    register(b, email="pa_other@co.example", company="Other Co")

    pid = _seed(ua["company_id"], name="Not Yours")
    assert b.patch(f"/api/products/{pid}", json={"public_access": True}).status_code == 404
    assert TestClient(api_module.app).get(f"/api/catalog/public/{pid}").status_code == 403


def test_toggle_does_not_create_a_version(auth_client):
    """Changing visibility is not a passport change."""
    client, user = auth_client
    pid = _seed(user["company_id"], name="No Version Please")

    client.patch(f"/api/products/{pid}", json={"public_access": True})
    assert client.get(f"/api/products/{pid}/versions").json() == []
