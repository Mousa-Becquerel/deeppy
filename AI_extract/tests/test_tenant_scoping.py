"""Multi-tenant isolation: user A must never see/touch user B's data."""

from fastapi.testclient import TestClient
import api as api_module


def _seed_product_for_company(company_id: str, name: str = "Test Product") -> str:
    """Insert a product directly via the repository (bypassing extraction)."""
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    with session_scope() as db:
        p = repo.create_product(db, passport={"overview": {"product_info": {
            "product_name": {"value": name, "confidence": "high"}
        }}}, completeness=50.0, source_documents=[], company_id=company_id)
        return p.id


def test_products_are_company_scoped(register):
    # Two independent companies / admins
    a_client = TestClient(api_module.app)
    _, user_a = register(a_client, email="a@co.example", company="Co A")
    b_client = TestClient(api_module.app)
    _, user_b = register(b_client, email="b@co.example", company="Co B")

    a_pid = _seed_product_for_company(user_a["company_id"], name="A's Product")
    b_pid = _seed_product_for_company(user_b["company_id"], name="B's Product")

    # A sees only A's product
    a_list = a_client.get("/api/products").json()
    a_ids = {p["id"] for p in a_list}
    assert a_pid in a_ids
    assert b_pid not in a_ids

    # B sees only B's product
    b_list = b_client.get("/api/products").json()
    b_ids = {p["id"] for p in b_list}
    assert b_pid in b_ids
    assert a_pid not in b_ids


def test_cannot_get_other_companys_product(register):
    a_client = TestClient(api_module.app)
    _, user_a = register(a_client, email="a2@co.example", company="Co A2")
    b_client = TestClient(api_module.app)
    register(b_client, email="b2@co.example", company="Co B2")

    a_pid = _seed_product_for_company(user_a["company_id"])
    # B cannot read it
    assert b_client.get(f"/api/products/{a_pid}").status_code == 404


def test_cannot_patch_other_companys_product(register):
    a_client = TestClient(api_module.app)
    _, user_a = register(a_client, email="a3@co.example", company="Co A3")
    b_client = TestClient(api_module.app)
    register(b_client, email="b3@co.example", company="Co B3")

    a_pid = _seed_product_for_company(user_a["company_id"])
    r = b_client.patch(f"/api/products/{a_pid}", json={"name": "hijacked"})
    assert r.status_code == 404


def test_cannot_delete_other_companys_product(register):
    a_client = TestClient(api_module.app)
    _, user_a = register(a_client, email="a4@co.example", company="Co A4")
    b_client = TestClient(api_module.app)
    register(b_client, email="b4@co.example", company="Co B4")

    a_pid = _seed_product_for_company(user_a["company_id"])
    assert b_client.delete(f"/api/products/{a_pid}").status_code == 404


def test_company_endpoint_returns_own_company_only(register):
    a_client = TestClient(api_module.app)
    register(a_client, email="cmp_a@co.example", company="Cmp Co A")
    b_client = TestClient(api_module.app)
    register(b_client, email="cmp_b@co.example", company="Cmp Co B")

    assert a_client.get("/api/company").json()["name"] == "Cmp Co A"
    assert b_client.get("/api/company").json()["name"] == "Cmp Co B"
