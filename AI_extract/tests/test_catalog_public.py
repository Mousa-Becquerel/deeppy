"""Session-less public catalog endpoints.

These back three things that must work for people who have never logged in:
  - GET /api/catalog/public                  — the landing page's DPP strip
  - GET /api/catalog/public/{ident}          — QR deep-link + /embed/<id>
  - GET /api/catalog/public/{ident}/image    — cover image for both

`ident` must resolve every form the UI hands out:
  - the uuid          — what ?dpp= QR deep-links encode
  - DPP-M-0002        — what the embed snippet and printed display ids use
  - a bare public_id  — tolerated for hand-written links

The DPP-M-0002 case is the important one: the original implementation only
handled the uuid and the bare integer, so the embed snippet the app copies to
the clipboard always 404'd and the iframe sat on a spinner forever. The tests
below build that identifier the same way the frontend does rather than
hardcoding a guess, so they break if either side changes format.

Route ordering also matters: /api/catalog/{product_id} is auth-gated and takes
a path parameter, so if the public routes are registered after it the literal
"public" gets captured as a product_id and everything here 401s.
"""
import os
from pathlib import Path

from fastapi.testclient import TestClient
import api as api_module


def _display_id(public_id: int, level: str = "M") -> str:
    """Mirror of dppId() in deeppy-v0_41.jsx:
        `${prefix}-${String(publicId).padStart(4, "0")}`
    Kept as a literal reimplementation so a format drift on either side shows
    up here instead of silently breaking embeds in production."""
    return f"DPP-{level}-{str(public_id).zfill(4)}"


def _seed(company_id: str, *, name: str, status: str = "published",
          public_access: bool = True, passport: dict | None = None) -> str:
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    from dpp_extractor.db import models as db_models
    with session_scope() as db:
        p = repo.create_product(
            db, passport=passport or {}, completeness=0.0,
            source_documents=[], company_id=company_id, status=status,
        )
        repo.update_product_fields(db, p.id, name=name)
        db.get(db_models.Product, p.id).public_access = public_access
        db.flush()
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


def test_public_list_still_shows_non_public_products(register):
    """Client spec: the others "can be shown like icon" — they stay listed,
    only the passport itself is gated."""
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_list_gated@co.example")
    gated = _seed(u["company_id"], name="Card Only", public_access=False)

    rows = {r["id"]: r for r in TestClient(api_module.app).get("/api/catalog/public").json()}
    assert gated in rows
    assert rows[gated]["public_access"] is False


def test_public_list_exposes_display_id(register):
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_list_did@co.example")
    pid = _seed(u["company_id"], name="Has Display Id")

    rows = {r["id"]: r for r in TestClient(api_module.app).get("/api/catalog/public").json()}
    assert rows[pid]["display_id"] == _display_id(_public_id_of(pid))


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


# ── detail: every identifier form the UI emits ─────────────────────────────


def test_public_detail_by_uuid(register):
    """The QR deep-link path: deeppy.eu/?dpp=<uuid>."""
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


def test_public_detail_by_display_id(register):
    """REGRESSION: DPP-M-0002 is what the embed snippet actually emits.

    The first implementation only handled uuid/bare-int, so this 404'd and the
    customer's iframe rendered a permanent spinner with no error.
    """
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_display@co.example")
    pid = _seed(u["company_id"], name="Embedded")
    did = _display_id(_public_id_of(pid))

    r = TestClient(api_module.app).get(f"/api/catalog/public/{did}")
    assert r.status_code == 200, f"{did} did not resolve: {r.text}"
    assert r.json()["id"] == pid


def test_public_detail_display_id_is_case_and_pad_insensitive(register):
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_display_fuzzy@co.example")
    pid = _seed(u["company_id"], name="Fuzzy")
    n = _public_id_of(pid)

    unauth = TestClient(api_module.app)
    for variant in (f"DPP-M-{n:04d}", f"dpp-m-{n:04d}", f"DPP-M-{n}", f"DPP-M-{n:08d}"):
        r = unauth.get(f"/api/catalog/public/{variant}")
        assert r.status_code == 200, f"{variant} failed to resolve"
        assert r.json()["id"] == pid


def test_public_detail_by_bare_public_id(register):
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_bare@co.example")
    pid = _seed(u["company_id"], name="Bare")

    r = TestClient(api_module.app).get(f"/api/catalog/public/{_public_id_of(pid)}")
    assert r.status_code == 200
    assert r.json()["id"] == pid


def test_batch_and_item_display_ids_do_not_resolve_as_models(register):
    """DPP-B-/DPP-I- must not silently fall through to a model lookup."""
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_wronglevel@co.example")
    pid = _seed(u["company_id"], name="Model Only")
    n = _public_id_of(pid)

    unauth = TestClient(api_module.app)
    assert unauth.get(f"/api/catalog/public/DPP-B-{n:04d}").status_code == 404
    assert unauth.get(f"/api/catalog/public/DPP-I-{n:04d}").status_code == 404


# ── gating ─────────────────────────────────────────────────────────────────


def test_public_detail_403_when_not_public(register):
    """Published but not flagged public: listed as a card, passport gated.
    403 not 404, so the UI can distinguish 'private' from 'missing'."""
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_gated@co.example")
    pid = _seed(u["company_id"], name="Gated", public_access=False)
    did = _display_id(_public_id_of(pid))

    unauth = TestClient(api_module.app)
    assert unauth.get(f"/api/catalog/public/{pid}").status_code == 403
    assert unauth.get(f"/api/catalog/public/{did}").status_code == 403


def test_public_detail_rejects_draft(register):
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_draft@co.example")
    draft = _seed(u["company_id"], name="Not Published", status="draft")

    unauth = TestClient(api_module.app)
    assert unauth.get(f"/api/catalog/public/{draft}").status_code == 404


def test_public_detail_unknown_ident_404():
    unauth = TestClient(api_module.app)
    assert unauth.get("/api/catalog/public/does-not-exist").status_code == 404
    assert unauth.get("/api/catalog/public/99999999").status_code == 404
    assert unauth.get("/api/catalog/public/DPP-M-9999").status_code == 404


def test_public_detail_payload_is_trimmed(register):
    """Internal bookkeeping must not ride along on a route with no session."""
    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_trim@co.example")
    pid = _seed(u["company_id"], name="Trimmed")

    body = TestClient(api_module.app).get(f"/api/catalog/public/{pid}").json()
    for leaked in ("source_documents", "documents", "has_eval_reference", "batches"):
        assert leaked not in body, f"{leaked} leaked on the public detail route"


# ── image endpoint ─────────────────────────────────────────────────────────


def test_public_image_by_uuid_and_display_id(register):
    uploads = Path(os.environ["UPLOADS_DIR"])
    img = uploads / "pub_cover.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\nrealbytes")

    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_img@co.example")
    pid = _seed(u["company_id"], name="Cover Product")
    _attach_image(pid, str(img))
    did = _display_id(_public_id_of(pid))

    unauth = TestClient(api_module.app)
    by_uuid = unauth.get(f"/api/catalog/public/{pid}/image")
    by_did = unauth.get(f"/api/catalog/public/{did}/image")
    assert by_uuid.status_code == 200, by_uuid.text
    assert by_did.status_code == 200, by_did.text
    assert by_uuid.content == b"\x89PNG\r\n\x1a\nrealbytes"
    assert by_did.content == by_uuid.content


def test_public_image_still_served_for_non_public_products(register):
    """The card/icon still renders for gated products, so its image must load
    even though the passport is 403."""
    uploads = Path(os.environ["UPLOADS_DIR"])
    img = uploads / "pub_gated_cover.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\nicon")

    owner = TestClient(api_module.app)
    _, u = register(owner, email="pub_img_gated@co.example")
    pid = _seed(u["company_id"], name="Gated Cover", public_access=False)
    _attach_image(pid, str(img))

    unauth = TestClient(api_module.app)
    assert unauth.get(f"/api/catalog/public/{pid}").status_code == 403
    assert unauth.get(f"/api/catalog/public/{pid}/image").status_code == 200


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
