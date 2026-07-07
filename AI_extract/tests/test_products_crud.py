"""Happy-path CRUD over the product endpoints."""

from fastapi.testclient import TestClient
import api as api_module


def _seed(company_id: str, name: str = "P") -> str:
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    with session_scope() as db:
        p = repo.create_product(db, passport={"overview": {}},
                                completeness=10.0, source_documents=[],
                                company_id=company_id)
        if name:
            repo.update_product_fields(db, p.id, name=name)
        return p.id


def test_list_products_empty_initially(auth_client):
    client, _ = auth_client
    r = client.get("/api/products")
    assert r.status_code == 200
    assert r.json() == []


def test_get_unknown_product_is_404(auth_client):
    client, _ = auth_client
    assert client.get("/api/products/does-not-exist").status_code == 404


def test_patch_product_renames(auth_client):
    client, user = auth_client
    pid = _seed(user["company_id"], name="Original")
    r = client.patch(f"/api/products/{pid}", json={"name": "Renamed"})
    assert r.status_code == 200
    assert r.json()["name"] == "Renamed"


def test_patch_product_passport_snapshots_version(auth_client):
    client, user = auth_client
    pid = _seed(user["company_id"])
    before = client.get(f"/api/products/{pid}/versions").json()
    new_passport = {"overview": {"product_info": {
        "product_name": {"value": "Edited", "confidence": "high"}
    }}}
    r = client.patch(f"/api/products/{pid}",
                     json={"passport": new_passport, "change_summary": "renamed via passport"})
    assert r.status_code == 200
    after = client.get(f"/api/products/{pid}/versions").json()
    assert len(after) == len(before) + 1


def test_delete_product_removes_it(auth_client):
    client, user = auth_client
    pid = _seed(user["company_id"])
    assert client.delete(f"/api/products/{pid}").status_code == 200
    assert client.get(f"/api/products/{pid}").status_code == 404


def test_delete_product_with_extraction_job_does_not_fk_fail(auth_client):
    """Regression: deleting a product that has an extraction_jobs row used to
    raise SQLite "FOREIGN KEY constraint failed" because the FK is nullable
    but without cascade. delete_product() now detaches the job first."""
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import models as db_models
    client, user = auth_client
    pid = _seed(user["company_id"])
    # Seed an extraction_jobs row pointing at this product (mimicking the
    # state any uploaded-and-extracted product is in).
    with session_scope() as db:
        db.add(db_models.ExtractionJob(
            id="job-deltest-1", product_id=pid, status="done", progress=100,
        ))
    assert client.delete(f"/api/products/{pid}").status_code == 200
    # Product is gone; job survives with product_id nulled.
    with session_scope() as db:
        assert db.get(db_models.Product, pid) is None
        job = db.get(db_models.ExtractionJob, "job-deltest-1")
        assert job is not None and job.product_id is None


def test_company_get_and_patch_roundtrip(auth_client):
    client, _ = auth_client
    r = client.patch("/api/company", json={"name": "New Name", "vat": "IT12345"})
    assert r.status_code == 200
    again = client.get("/api/company").json()
    assert again["name"] == "New Name"
    assert again["vat"] == "IT12345"


def test_list_products_returns_seeded(auth_client):
    client, user = auth_client
    pid = _seed(user["company_id"], name="Listed")
    listed = client.get("/api/products").json()
    assert any(p["id"] == pid and p["name"] == "Listed" for p in listed)
