"""Bucket 7 Tier D — batch accounting endpoints.

Covers:
  - GET  /api/batches                                — company-scoped list,
                                                       optional family_code
                                                       filter (Option A picker)
  - GET  /api/batches/{id}/availability              — live remaining_quantity
  - PATCH /api/batches/{id}                          — edit available_quantity,
                                                       available_unit, overrides
  - repo.batch_consumed_quantity                     — live sum of every OTHER
                                                       batch's required_quantity
                                                       pointing at this one
  - public_id backfill / next-id semantics on create — auto-increment per table
"""
from __future__ import annotations

import api as api_module
from fastapi.testclient import TestClient


def _make_product(company_id: str, family_code: str | None = None, name: str = "Test Product") -> str:
    """Insert a product row directly via the repo so we don't have to run
    extraction. Returns the product uuid."""
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    with session_scope() as db:
        passport = {"overview": {"product_info": {"product_name": {"value": name}}}}
        if family_code:
            passport["overview"]["product_info"]["product_family_code"] = {"value": family_code}
        p = repo.create_product(
            db, passport=passport, completeness=0.0, source_documents=[],
            company_id=company_id, status="draft",
        )
        # derive_hot_columns pulls name from the passport, but family_code
        # is fetched from a different path; set it explicitly if provided.
        if family_code:
            p.family_code = family_code
            db.flush()
        return p.id


def _make_batch(product_id: str, lot: str = "L-1",
                available_quantity: float | None = None,
                available_unit: str | None = None) -> str:
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    with session_scope() as db:
        b = repo.create_batch(
            db, product_id, lot=lot,
            available_quantity=available_quantity,
            available_unit=available_unit,
        )
        return b.id


# ── public_id assignment ───────────────────────────────────────────────────


def test_product_gets_incremental_public_id(auth_client):
    client, user = auth_client
    a = _make_product(user["company_id"], name="A")
    b = _make_product(user["company_id"], name="B")
    from dpp_extractor.db import session_scope, models
    with session_scope() as db:
        pa = db.get(models.Product, a)
        pb = db.get(models.Product, b)
        assert pa.public_id is not None
        assert pb.public_id == pa.public_id + 1


def test_batch_gets_incremental_public_id(auth_client):
    client, user = auth_client
    pid = _make_product(user["company_id"])
    b1 = _make_batch(pid, lot="L1")
    b2 = _make_batch(pid, lot="L2")
    from dpp_extractor.db import session_scope, models
    with session_scope() as db:
        assert db.get(models.Batch, b1).public_id + 1 == db.get(models.Batch, b2).public_id


# ── GET /api/batches ───────────────────────────────────────────────────────


def test_list_batches_returns_own_company_only(register):
    a_client = TestClient(api_module.app)
    _, ua = register(a_client, email="ba@co.example", company="A")
    b_client = TestClient(api_module.app)
    _, ub = register(b_client, email="bb@co.example", company="B")

    pa = _make_product(ua["company_id"], name="ProdA")
    _make_batch(pa, lot="A-1")
    pb = _make_product(ub["company_id"], name="ProdB")
    _make_batch(pb, lot="B-1")

    a_rows = a_client.get("/api/batches").json()
    assert {r["lot"] for r in a_rows} == {"A-1"}
    b_rows = b_client.get("/api/batches").json()
    assert {r["lot"] for r in b_rows} == {"B-1"}


def test_list_batches_filters_by_family_code(auth_client):
    client, user = auth_client
    cem_pid = _make_product(user["company_id"], family_code="CEM", name="Cement product")
    mas_pid = _make_product(user["company_id"], family_code="MAS", name="Masonry product")
    _make_batch(cem_pid, lot="cem-1")
    _make_batch(mas_pid, lot="mas-1")

    cem_rows = client.get("/api/batches?family_code=CEM").json()
    assert {r["lot"] for r in cem_rows} == {"cem-1"}
    # Wrong code returns empty (not all batches).
    empty = client.get("/api/batches?family_code=NOPE").json()
    assert empty == []


def test_list_batches_includes_parent_context_and_remaining(auth_client):
    client, user = auth_client
    pid = _make_product(user["company_id"], family_code="CEM", name="Almond shell #1")
    bid = _make_batch(pid, lot="AS-1", available_quantity=500.0, available_unit="kg")

    rows = client.get("/api/batches").json()
    row = next(r for r in rows if r["id"] == bid)
    assert row["parent_product_name"] == "Almond shell #1"
    assert row["parent_family_code"] == "CEM"
    assert row["available_quantity"] == 500.0
    assert row["available_unit"] == "kg"
    # No parents claim it → remaining == available.
    assert row["consumed_quantity"] == 0.0
    assert row["remaining_quantity"] == 500.0
    assert row["public_id"] is not None


# ── PATCH /api/batches/{id} ────────────────────────────────────────────────


def test_patch_batch_updates_quantity_and_unit(auth_client):
    client, user = auth_client
    pid = _make_product(user["company_id"])
    bid = _make_batch(pid, lot="L1")

    r = client.patch(f"/api/batches/{bid}", json={
        "available_quantity": 42.5, "available_unit": "kg",
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["available_quantity"] == 42.5
    assert body["available_unit"] == "kg"


def test_patch_batch_replaces_overrides_dict(auth_client):
    client, user = auth_client
    pid = _make_product(user["company_id"])
    bid = _make_batch(pid, lot="L1")

    r = client.patch(f"/api/batches/{bid}", json={
        "overrides": {"composition_links": {"Material#1": {"linked_batch_uuid": "abc"}}},
    })
    assert r.status_code == 200
    assert r.json()["overrides"]["composition_links"]["Material#1"]["linked_batch_uuid"] == "abc"


def test_patch_batch_404_cross_company(register):
    a_client = TestClient(api_module.app)
    _, ua = register(a_client, email="patcha@co.example", company="A")
    b_client = TestClient(api_module.app)
    register(b_client, email="patchb@co.example", company="B")

    pid = _make_product(ua["company_id"])
    bid = _make_batch(pid, lot="A-only")
    # B tries to edit A's batch.
    r = b_client.patch(f"/api/batches/{bid}", json={"available_quantity": 1})
    assert r.status_code == 404


# ── GET /api/batches/{id}/availability + consumed_quantity ─────────────────


def test_availability_of_uncomsumed_batch_equals_available(auth_client):
    client, user = auth_client
    pid = _make_product(user["company_id"])
    bid = _make_batch(pid, lot="L1", available_quantity=100.0, available_unit="kg")

    body = client.get(f"/api/batches/{bid}/availability").json()
    assert body["available_quantity"] == 100.0
    assert body["consumed_quantity"] == 0.0
    assert body["remaining_quantity"] == 100.0
    assert body["available_unit"] == "kg"


def test_availability_subtracts_parent_requirements(auth_client):
    """The canonical scenario from the client's document: parent BATCH links
    a composition row to a child BATCH; child's remaining decreases by the
    parent's required_quantity."""
    client, user = auth_client
    # Child batch: almond shell #1, 500 kg total.
    child_pid = _make_product(user["company_id"], name="Almond shell #1")
    child_bid = _make_batch(child_pid, lot="AS-1", available_quantity=500.0, available_unit="kg")

    # Two parent batches consuming 200 kg + 100 kg → child remaining = 200 kg.
    parent_pid = _make_product(user["company_id"], name="Biomortar")
    p1 = _make_batch(parent_pid, lot="BM-1")
    p2 = _make_batch(parent_pid, lot="BM-2")

    # Wire the consumption via composition.materials on each parent's overrides.
    for pid, needed in ((p1, 200.0), (p2, 100.0)):
        r = client.patch(f"/api/batches/{pid}", json={
            "overrides": {"composition": {"materials": [{
                "material_id": "Material#1",
                "linked_batch_uuid": child_bid,
                "required_quantity": needed,
                "required_unit": "kg",
            }]}},
        })
        assert r.status_code == 200, r.text

    body = client.get(f"/api/batches/{child_bid}/availability").json()
    assert body["available_quantity"] == 500.0
    assert body["consumed_quantity"] == 300.0
    assert body["remaining_quantity"] == 200.0


def test_availability_ignores_own_batch_composition(auth_client):
    """A batch that lists ITSELF in its composition (weird but possible via
    editor mistake) should not consume from its own remaining count."""
    client, user = auth_client
    pid = _make_product(user["company_id"])
    bid = _make_batch(pid, lot="Self", available_quantity=50.0, available_unit="kg")
    r = client.patch(f"/api/batches/{bid}", json={
        "overrides": {"composition": {"materials": [{
            "material_id": "Material#1",
            "linked_batch_uuid": bid,          # links to itself
            "required_quantity": 30.0,
        }]}},
    })
    assert r.status_code == 200
    body = client.get(f"/api/batches/{bid}/availability").json()
    assert body["consumed_quantity"] == 0.0   # skipped because id == self
    assert body["remaining_quantity"] == 50.0


def test_availability_404_cross_company(register):
    a_client = TestClient(api_module.app)
    _, ua = register(a_client, email="avail_a@co.example", company="A")
    b_client = TestClient(api_module.app)
    register(b_client, email="avail_b@co.example", company="B")

    pid = _make_product(ua["company_id"])
    bid = _make_batch(pid, lot="L1", available_quantity=10.0)
    assert b_client.get(f"/api/batches/{bid}/availability").status_code == 404


def test_availability_null_quantity_returns_null_remaining(auth_client):
    """Batches without a quantity yet (user hasn't set it) should return
    None for both available_quantity and remaining_quantity, not zero."""
    client, user = auth_client
    pid = _make_product(user["company_id"])
    bid = _make_batch(pid, lot="Unset")
    body = client.get(f"/api/batches/{bid}/availability").json()
    assert body["available_quantity"] is None
    assert body["remaining_quantity"] is None


# ── Batch detail carries new fields ────────────────────────────────────────


def test_batch_detail_includes_public_id_and_quantity(auth_client):
    client, user = auth_client
    pid = _make_product(user["company_id"])
    bid = _make_batch(pid, lot="L1", available_quantity=25.0, available_unit="t")

    # Fetch via the product detail endpoint which lists batches.
    body = client.get(f"/api/products/{pid}").json()
    b = next(b for b in body["batches"] if b["id"] == bid)
    assert b["public_id"] is not None
    assert b["available_quantity"] == 25.0
    assert b["available_unit"] == "t"
