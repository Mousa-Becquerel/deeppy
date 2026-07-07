"""B2 verification: document-fetch refuses storage_paths outside UPLOADS_DIR."""

import os
from pathlib import Path

from fastapi.testclient import TestClient
import api as api_module


def _seed_product_and_evil_doc(company_id: str, evil_path: str) -> tuple[str, str]:
    """Insert a product + a tampered Document whose storage_path escapes uploads."""
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    from dpp_extractor.db import models as db_models
    with session_scope() as db:
        p = repo.create_product(db, passport={}, completeness=0.0,
                                source_documents=[], company_id=company_id)
        doc = db_models.Document(
            product_id=p.id,
            filename="totally_legit.pdf",
            storage_path=evil_path,
            doc_type="datasheet",
        )
        db.add(doc)
        db.flush()
        return p.id, doc.id


def test_document_fetch_rejects_path_outside_uploads(register, tmp_path):
    """A document whose storage_path lives outside UPLOADS_DIR returns 404,
    even if the file exists on disk."""
    client = TestClient(api_module.app)
    _, admin = register(client, email="trav1@co.example")

    # Create a real file *outside* the uploads directory the app is configured for.
    outside = tmp_path / "secret.txt"
    outside.write_text("super-secret")

    pid, did = _seed_product_and_evil_doc(admin["company_id"], str(outside))
    r = client.get(f"/api/products/{pid}/documents/{did}")
    assert r.status_code == 404


def test_document_fetch_rejects_traversal_with_dotdot(register):
    """A storage_path containing ../../ resolves outside uploads → 404."""
    client = TestClient(api_module.app)
    _, admin = register(client, email="trav2@co.example")

    evil = os.environ["UPLOADS_DIR"] + "/../../../../etc/passwd"
    pid, did = _seed_product_and_evil_doc(admin["company_id"], evil)
    r = client.get(f"/api/products/{pid}/documents/{did}")
    assert r.status_code == 404


def test_document_fetch_works_for_legit_path(register):
    """Control: a storage_path inside UPLOADS_DIR with a real file returns 200."""
    client = TestClient(api_module.app)
    _, admin = register(client, email="trav3@co.example")

    uploads = Path(os.environ["UPLOADS_DIR"])
    good = uploads / "doc_ok.txt"
    good.write_bytes(b"hello world")

    pid, did = _seed_product_and_evil_doc(admin["company_id"], str(good))
    r = client.get(f"/api/products/{pid}/documents/{did}")
    assert r.status_code == 200
    assert r.content == b"hello world"
