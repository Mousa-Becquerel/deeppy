"""GET /api/catalog — cross-company visibility, drafts excluded, KPI shape."""

from fastapi.testclient import TestClient
import api as api_module


def _seed(company_id: str, *, name: str, status: str = "draft",
          passport: dict | None = None) -> str:
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    with session_scope() as db:
        p = repo.create_product(
            db, passport=passport or {}, completeness=0.0,
            source_documents=[], company_id=company_id, status=status,
        )
        repo.update_product_fields(db, p.id, name=name)
        return p.id


def test_catalog_returns_published_from_all_companies(register):
    a_client = TestClient(api_module.app)
    _, ua = register(a_client, email="cat_a@co.example", company="Co A")
    b_client = TestClient(api_module.app)
    _, ub = register(b_client, email="cat_b@co.example", company="Co B")

    pid_a = _seed(ua["company_id"], name="A Pub", status="published")
    pid_b = _seed(ub["company_id"], name="B Pub", status="published")

    # Both viewers see both products.
    a_list = a_client.get("/api/catalog").json()
    b_list = b_client.get("/api/catalog").json()
    ids_a = {row["id"] for row in a_list}
    ids_b = {row["id"] for row in b_list}
    assert pid_a in ids_a and pid_b in ids_a
    assert pid_a in ids_b and pid_b in ids_b


def test_catalog_marks_is_own_correctly(register):
    a_client = TestClient(api_module.app)
    _, ua = register(a_client, email="cat_own_a@co.example", company="Own A")
    b_client = TestClient(api_module.app)
    register(b_client, email="cat_own_b@co.example", company="Own B")

    pid_a = _seed(ua["company_id"], name="Belongs to A", status="published")

    a_rows = {r["id"]: r for r in a_client.get("/api/catalog").json()}
    b_rows = {r["id"]: r for r in b_client.get("/api/catalog").json()}
    assert a_rows[pid_a]["is_own"] is True
    assert b_rows[pid_a]["is_own"] is False


def test_catalog_excludes_drafts(register):
    client = TestClient(api_module.app)
    _, u = register(client, email="cat_draft@co.example")
    pub_id = _seed(u["company_id"], name="Visible Pub", status="published")
    draft_id = _seed(u["company_id"], name="Hidden Draft", status="draft")

    ids = {r["id"] for r in client.get("/api/catalog").json()}
    assert pub_id in ids
    assert draft_id not in ids


def test_catalog_requires_auth():
    unauth = TestClient(api_module.app)
    assert unauth.get("/api/catalog").status_code == 401


def test_catalog_includes_company_name(register):
    client = TestClient(api_module.app)
    _, u = register(client, email="cat_named@co.example", company="My Display Co")
    pid = _seed(u["company_id"], name="X", status="published")
    rows = {r["id"]: r for r in client.get("/api/catalog").json()}
    assert rows[pid]["company_name"] == "My Display Co"


def test_catalog_kpis_extract_recycled_and_gwp(register):
    client = TestClient(api_module.app)
    _, u = register(client, email="cat_kpi@co.example")
    passport = {
        "performance": {"values": [
            {"property_name": "Compressive strength", "value": {"value": "10"}},
            {"property_name": "Recycled content",
             "value": {"value": "72", "confidence": "high"}},
        ]},
        "lifecycle": {"stages": [
            {"stage_code": "A1-A3", "gwp_total": {"value": 5.5}},
            {"stage_code": "C3",    "gwp_total": {"value": 0.5}},
            {"stage_code": "D",     "gwp_total": {"value": None}},
        ]},
    }
    pid = _seed(u["company_id"], name="Kpi Test", status="published",
                passport=passport)
    row = next(r for r in client.get("/api/catalog").json() if r["id"] == pid)
    assert row["kpis"]["recycled"] == "72%"
    assert row["kpis"]["gwp_total"] == 6.0  # 5.5 + 0.5, None skipped
    assert row["kpis"]["energy_class"] is None


def test_catalog_kpis_empty_when_passport_empty(register):
    client = TestClient(api_module.app)
    _, u = register(client, email="cat_empty@co.example")
    pid = _seed(u["company_id"], name="Empty", status="published", passport={})
    row = next(r for r in client.get("/api/catalog").json() if r["id"] == pid)
    assert row["kpis"] == {"gwp_total": None, "recycled": None, "energy_class": None}


def test_catalog_detail_returns_published_cross_tenant(register):
    a_client = TestClient(api_module.app)
    _, ua = register(a_client, email="cat_det_a@co.example", company="DetA")
    b_client = TestClient(api_module.app)
    register(b_client, email="cat_det_b@co.example", company="DetB")
    pid_a = _seed(ua["company_id"], name="Cross Detail", status="published",
                  passport={"overview": {"product_info": {
                      "product_name": {"value": "Cross Detail", "confidence": "high"}
                  }}})
    # B can fetch A's published product via /catalog/{id}
    r = b_client.get(f"/api/catalog/{pid_a}")
    assert r.status_code == 200
    assert r.json()["name"] == "Cross Detail"


def test_catalog_detail_404_for_draft(register):
    client = TestClient(api_module.app)
    _, u = register(client, email="cat_det_draft@co.example")
    pid = _seed(u["company_id"], name="Draft Hidden", status="draft")
    # Even the OWNER can't access via /catalog/ — that endpoint is published-only.
    assert client.get(f"/api/catalog/{pid}").status_code == 404
