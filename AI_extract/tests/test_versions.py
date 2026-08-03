"""Version edit/delete endpoints — client feedback item 12.

Auto-generated version labels ('v1', 'v2') and change summaries ('Manual edit')
weren't accurate for the tester's workflow; they need to rewrite them and
sometimes remove unwanted auto-snapshots. These endpoints back that UX.
"""
import api as api_module
from fastapi.testclient import TestClient


def _seed_version(product_id: str, label: str = "v1", change: str = "auto snap"):
    """Create a version row directly via the repo. Returns its id."""
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    with session_scope() as db:
        v = repo.create_version(
            db, product_id,
            passport_snapshot={"overview": {}},
            label=label, change_summary=change,
        )
        return v.id


def _seed_product(company_id: str) -> str:
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    with session_scope() as db:
        p = repo.create_product(
            db, passport={}, completeness=0.0, source_documents=[],
            company_id=company_id, status="draft",
        )
        return p.id


# ─── list (regression) ────────────────────────────────────────────────────

def test_list_versions_returns_seeded(auth_client):
    client, user = auth_client
    pid = _seed_product(user["company_id"])
    _seed_version(pid, label="v1", change="first")
    _seed_version(pid, label="v2", change="second")
    r = client.get(f"/api/products/{pid}/versions")
    assert r.status_code == 200
    versions = r.json()
    assert len(versions) == 2
    assert {v["label"] for v in versions} == {"v1", "v2"}


# ─── PATCH ─────────────────────────────────────────────────────────────────

def test_patch_version_updates_label_and_summary(auth_client):
    client, user = auth_client
    pid = _seed_product(user["company_id"])
    vid = _seed_version(pid, label="v1", change="Manual edit")

    r = client.patch(
        f"/api/products/{pid}/versions/{vid}",
        json={"label": "Released to CE audit", "change_summary": "Fixed GWP after re-testing"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["label"] == "Released to CE audit"
    assert body["change_summary"] == "Fixed GWP after re-testing"


def test_patch_version_empty_string_clears_field(auth_client):
    """Sending '' should NULL the field so it renders as blank rather than
    keeping the auto-generated placeholder."""
    client, user = auth_client
    pid = _seed_product(user["company_id"])
    vid = _seed_version(pid, label="v1", change="auto")
    r = client.patch(
        f"/api/products/{pid}/versions/{vid}",
        json={"label": "", "change_summary": ""},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["label"] is None
    assert body["change_summary"] is None


def test_patch_version_partial(auth_client):
    """Only updating label leaves change_summary alone."""
    client, user = auth_client
    pid = _seed_product(user["company_id"])
    vid = _seed_version(pid, label="v1", change="original summary")
    r = client.patch(f"/api/products/{pid}/versions/{vid}", json={"label": "renamed"})
    assert r.status_code == 200
    assert r.json()["label"] == "renamed"
    assert r.json()["change_summary"] == "original summary"


def test_patch_version_404_for_wrong_product(auth_client):
    """Version id must belong to the URL's product_id."""
    client, user = auth_client
    pid_a = _seed_product(user["company_id"])
    pid_b = _seed_product(user["company_id"])
    vid_a = _seed_version(pid_a, label="v1")
    assert client.patch(f"/api/products/{pid_b}/versions/{vid_a}",
                        json={"label": "x"}).status_code == 404


def test_patch_version_404_cross_company(register):
    """User B cannot edit user A's versions."""
    a_client = TestClient(api_module.app)
    _, ua = register(a_client, email="ver_a@co.example", company="V-Co-A")
    b_client = TestClient(api_module.app)
    register(b_client, email="ver_b@co.example", company="V-Co-B")

    pid = _seed_product(ua["company_id"])
    vid = _seed_version(pid, label="v1")
    assert b_client.patch(f"/api/products/{pid}/versions/{vid}",
                          json={"label": "hijack"}).status_code == 404


# ─── DELETE ────────────────────────────────────────────────────────────────

def test_delete_version_removes_it(auth_client):
    client, user = auth_client
    pid = _seed_product(user["company_id"])
    vid = _seed_version(pid, label="unwanted auto-snap")

    r = client.delete(f"/api/products/{pid}/versions/{vid}")
    assert r.status_code == 200
    # Now the list shouldn't include it.
    listed = client.get(f"/api/products/{pid}/versions").json()
    assert all(v["id"] != vid for v in listed)


def test_delete_version_404_cross_company(register):
    a_client = TestClient(api_module.app)
    _, ua = register(a_client, email="ver_d_a@co.example", company="D-A")
    b_client = TestClient(api_module.app)
    register(b_client, email="ver_d_b@co.example", company="D-B")

    pid = _seed_product(ua["company_id"])
    vid = _seed_version(pid, label="v1")
    assert b_client.delete(f"/api/products/{pid}/versions/{vid}").status_code == 404


def test_delete_version_404_missing():
    """Non-existent version id in the URL 404s (auth still enforced)."""
    from fastapi.testclient import TestClient
    unauth = TestClient(api_module.app)
    r = unauth.delete("/api/products/nope/versions/also-nope")
    assert r.status_code == 401  # auth-gated before route logic
