"""Session-less public catalog endpoints (Sept 18 client feedback).

These back two things that must work for people who have never logged in:
  - GET /api/catalog/public                  — the landing page's published
                                               DPP strip
  - GET /api/catalog/public/{ident}          — the QR deep-link target and the
                                               /embed/<id> widget
  - GET /api/catalog/public/{ident}/image    — cover image for both of the above

`ident` resolves as either the product uuid (what QR codes encode) or the
friendly incremental public_id (what the embed snippet encodes).

Route ordering matters here: /api/catalog/{product_id} is auth-gated and
declared with a path parameter, so if the public routes were registered after
it, the literal "public" would be captured as a product_id and every one of
these would 401. Several of these tests fail loudly if that regresses.
"""
import os
from pathlib import Path

from fastapi.testclient import TestClient
import api as api_module


def _seed(company_id: str, *, name: str, status: str = "published",
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


def _public_id_of(product_id: str) -> int:
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import models as db_models
    with session_scope() as db:
        return db.get(db_models.Product, product_id).public_id


def _attach_image(product_id: str, storage_path: str, filename: str = "cover.png") -> str:
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import models as db_models
    with session_scope() as db:
        doc = db_models.Document(
            product_id=product_id, filename=filename,
            storage_path=storage_path, doc_type="product_image",
        )
        db.add(doc)
        db.flush()
        return doc.id


# ── list endpoint ──────────────────────────────────────────────────────────


def test_public_list_needs_no_session(register):
    """The auth-gated sibling 401s; this one must not."""
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_list@co.example", company="Pub Co")
    pid = _seed(u["company_id"], name="Public Strip Product")

    unauth = TestClient(api_module.app)
    assert unauth.get("/api/catalog").status_code == 401     # guard still holds

    r = unauth.get("/api/catalog/public")
    assert r.status_code == 200, r.text
    assert pid in {row["id"] for row in r.json()}


def test_public_list_excludes_drafts(register):
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_list_draft@co.example")
    pub = _seed(u["company_id"], name="Shown", status="published")
    draft = _seed(u["company_id"], name="Hidden", status="draft")

    ids = {r["id"] for r in TestClient(api_module.app).get("/api/catalog/public").json()}
    assert pub in ids
    assert draft not in ids


def test_public_list_caps_at_twelve(register):
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_cap@co.example")
    for i in range(15):
        _seed(u["company_id"], name=f"Capped {i}")

    rows = TestClient(api_module.app).get("/api/catalog/public").json()
    assert len(rows) <= 12


def test_public_list_image_url_points_at_public_route(register):
    """Must not hand out /api/catalog/{id}/documents/{id} — that's auth-gated,
    so anonymous visitors would get broken images on the landing page."""
    uploads = Path(os.environ["UPLOADS_DIR"])
    img = uploads / "pub_list_cover.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\nfake")

    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_list_img@co.example")
    pid = _seed(u["company_id"], name="Has Cover")
    _attach_image(pid, str(img))

    rows = {r["id"]: r for r in TestClient(api_module.app).get("/api/catalog/public").json()}
    assert rows[pid]["image_url"] == f"/api/catalog/public/{pid}/image"


# ── detail endpoint: uuid (QR) and public_id (embed) ───────────────────────


def test_public_detail_by_uuid_needs_no_session(register):
    """This is the QR deep-link path: deeppy.eu/?dpp=<uuid>."""
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_uuid@co.example")
    passport = {"overview": {"product_info": {"product_name": {"value": "Scanned"}}}}
    pid = _seed(u["company_id"], name="Scanned", passport=passport)

    r = TestClient(api_module.app).get(f"/api/catalog/public/{pid}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["id"] == pid
    assert body["passport"] is not None
    assert body["stats"] is not None


def test_public_detail_by_public_id_needs_no_session(register):
    """This is the embed path: deeppy.eu/embed/<public_id>. The snippet the
    app copies to the clipboard uses public_id, NOT the uuid."""
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_pubid@co.example")
    pid = _seed(u["company_id"], name="Embedded")
    puid = _public_id_of(pid)

    r = TestClient(api_module.app).get(f"/api/catalog/public/{puid}")
    assert r.status_code == 200, r.text
    assert r.json()["id"] == pid          # same product, resolved two ways


def test_public_detail_rejects_draft(register):
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_draft@co.example")
    draft = _seed(u["company_id"], name="Not Published", status="draft")
    puid = _public_id_of(draft)

    unauth = TestClient(api_module.app)
    assert unauth.get(f"/api/catalog/public/{draft}").status_code == 404
    assert unauth.get(f"/api/catalog/public/{puid}").status_code == 404


def test_public_detail_unknown_ident_404():
    unauth = TestClient(api_module.app)
    assert unauth.get("/api/catalog/public/does-not-exist").status_code == 404
    assert unauth.get("/api/catalog/public/99999999").status_code == 404


def test_public_detail_payload_is_trimmed(register):
    """Internal bookkeeping must not ride along on a route with no session."""
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_trim@co.example")
    pid = _seed(u["company_id"], name="Trimmed")

    body = TestClient(api_module.app).get(f"/api/catalog/public/{pid}").json()
    for leaked in ("source_documents", "documents", "has_eval_reference", "batches"):
        assert leaked not in body, f"{leaked} leaked on the public detail route"


# ── image endpoint ─────────────────────────────────────────────────────────


def test_public_image_by_uuid_and_public_id(register):
    uploads = Path(os.environ["UPLOADS_DIR"])
    img = uploads / "pub_cover.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\nrealbytes")

    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_img@co.example")
    pid = _seed(u["company_id"], name="Cover Product")
    _attach_image(pid, str(img))
    puid = _public_id_of(pid)

    unauth = TestClient(api_module.app)
    by_uuid = unauth.get(f"/api/catalog/public/{pid}/image")
    by_puid = unauth.get(f"/api/catalog/public/{puid}/image")
    assert by_uuid.status_code == 200, by_uuid.text
    assert by_puid.status_code == 200, by_puid.text
    assert by_uuid.content == b"\x89PNG\r\n\x1a\nrealbytes"
    assert by_puid.content == by_uuid.content


def test_public_image_404_for_draft(register):
    uploads = Path(os.environ["UPLOADS_DIR"])
    img = uploads / "pub_draft_cover.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\nhidden")

    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_img_draft@co.example")
    pid = _seed(u["company_id"], name="Draft Cover", status="draft")
    _attach_image(pid, str(img))

    assert TestClient(api_module.app).get(f"/api/catalog/public/{pid}/image").status_code == 404


def test_public_image_escapes_uploads_root_are_rejected(register):
    """Same path-traversal guard as the auth-gated document route."""
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_img_trav@co.example")
    pid = _seed(u["company_id"], name="Traversal")
    _attach_image(pid, "/etc/passwd", filename="passwd.png")

    assert TestClient(api_module.app).get(f"/api/catalog/public/{pid}/image").status_code == 404
