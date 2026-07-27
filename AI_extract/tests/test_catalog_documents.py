"""GET /api/catalog/{pid}/documents/{did} — public catalog document download.

Same B2 path-traversal guard as /api/products/{}/documents/{}, but cross-tenant
(any logged-in user can download from any published product's docs).
"""
import os
from pathlib import Path

from fastapi.testclient import TestClient
import api as api_module


def _seed_product_with_doc(
    company_id: str, *, status: str, storage_path: str, filename: str = "hello.txt",
) -> tuple[str, str]:
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    from dpp_extractor.db import models as db_models
    with session_scope() as db:
        p = repo.create_product(
            db, passport={}, completeness=0.0, source_documents=[],
            company_id=company_id, status=status,
        )
        doc = db_models.Document(
            product_id=p.id, filename=filename,
            storage_path=storage_path, doc_type="datasheet",
        )
        db.add(doc)
        db.flush()
        return p.id, doc.id


def test_catalog_document_download_cross_tenant(register):
    """User B can download a document attached to user A's PUBLISHED product."""
    uploads = Path(os.environ["UPLOADS_DIR"])
    good = uploads / "cat_doc_ok.txt"
    good.write_bytes(b"content of published doc")

    a_client = TestClient(api_module.app)
    _, ua = register(a_client, email="cd_a@co.example", company="Co Cat A")
    b_client = TestClient(api_module.app)
    register(b_client, email="cd_b@co.example", company="Co Cat B")

    pid, did = _seed_product_with_doc(
        ua["company_id"], status="published", storage_path=str(good),
        filename="hello.txt",
    )

    r = b_client.get(f"/api/catalog/{pid}/documents/{did}")
    assert r.status_code == 200
    assert r.content == b"content of published doc"


def test_catalog_document_download_404_for_draft(register):
    """Drafts are NOT downloadable through the catalog path, even by owner."""
    uploads = Path(os.environ["UPLOADS_DIR"])
    good = uploads / "cat_doc_draft.txt"
    good.write_bytes(b"draft content")

    client = TestClient(api_module.app)
    _, u = register(client, email="cd_draft@co.example")
    pid, did = _seed_product_with_doc(
        u["company_id"], status="draft", storage_path=str(good),
    )

    assert client.get(f"/api/catalog/{pid}/documents/{did}").status_code == 404


def test_catalog_document_download_requires_auth():
    unauth = TestClient(api_module.app)
    r = unauth.get("/api/catalog/some-pid/documents/some-did")
    assert r.status_code == 401


def test_catalog_document_path_traversal_rejected(register):
    """Storage path outside UPLOADS_DIR must 404 even for published products."""
    client = TestClient(api_module.app)
    _, u = register(client, email="cd_trav@co.example")
    # Craft an evil storage_path outside the uploads volume.
    evil = os.environ["UPLOADS_DIR"] + "/../../etc/passwd"
    pid, did = _seed_product_with_doc(
        u["company_id"], status="published", storage_path=evil,
    )
    assert client.get(f"/api/catalog/{pid}/documents/{did}").status_code == 404


def test_catalog_document_404_when_doc_belongs_to_other_product(register):
    """A did that belongs to a different product returns 404 even if both
    products are published (product_id/doc_id mismatch)."""
    uploads = Path(os.environ["UPLOADS_DIR"])
    good = uploads / "cat_doc_mix.txt"
    good.write_bytes(b"x")

    client = TestClient(api_module.app)
    _, u = register(client, email="cd_mix@co.example")
    pid_a, did_a = _seed_product_with_doc(
        u["company_id"], status="published", storage_path=str(good),
    )
    pid_b, _ = _seed_product_with_doc(
        u["company_id"], status="published", storage_path=str(good),
    )
    # Ask for did_a under pid_b — should 404.
    assert client.get(f"/api/catalog/{pid_b}/documents/{did_a}").status_code == 404
