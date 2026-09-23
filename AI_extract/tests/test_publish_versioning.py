"""Republishing a DPP must leave a version behind.

Client, Sept 23: "The 'version' tab is not working. Every time a DPP is
republished, we should keep track of it."

The Versions tab itself was fine — it was always empty. The publish button
PATCHes {"status": "published"} with no passport, and the snapshot branch in
update_product only ran when body.passport was present, so publishing never
recorded anything. These tests pin the publish path specifically, separately
from the already-covered save-edits path.
"""
from fastapi.testclient import TestClient
import api as api_module


def _seed_draft(company_id: str, name: str = "Draft Product") -> str:
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    with session_scope() as db:
        p = repo.create_product(
            db,
            passport={"overview": {"product_info": {"product_name": {"value": name}}}},
            completeness=0.0, source_documents=[],
            company_id=company_id, status="draft",
        )
        repo.update_product_fields(db, p.id, name=name)
        return p.id


def test_publish_creates_a_version(auth_client):
    """This is the exact request the publish button sends."""
    client, user = auth_client
    pid = _seed_draft(user["company_id"], "Publish Me")

    assert client.get(f"/api/products/{pid}/versions").json() == []

    r = client.patch(f"/api/products/{pid}", json={"status": "published"})
    assert r.status_code == 200, r.text

    versions = client.get(f"/api/products/{pid}/versions").json()
    assert len(versions) == 1, "publishing left no version behind"
    assert versions[0]["label"] == "v1"
    assert versions[0]["change_summary"] == "Published"


def test_each_republish_adds_a_version(auth_client):
    """"Every time a DPP is republished" — three publishes, three versions."""
    client, user = auth_client
    pid = _seed_draft(user["company_id"], "Republish Me")

    for _ in range(3):
        assert client.patch(f"/api/products/{pid}", json={"status": "published"}).status_code == 200

    versions = client.get(f"/api/products/{pid}/versions").json()
    assert len(versions) == 3
    assert {v["label"] for v in versions} == {"v1", "v2", "v3"}


def test_publish_snapshots_the_current_passport(auth_client):
    """The snapshot must capture the passport as it stands at publish time,
    not an empty dict — otherwise restoring a version would wipe the DPP."""
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo

    client, user = auth_client
    pid = _seed_draft(user["company_id"], "Snapshot Me")
    client.patch(f"/api/products/{pid}", json={"status": "published"})

    with session_scope() as db:
        stored = repo.list_versions(db, pid)
        assert len(stored) == 1
        snap = stored[0].passport_snapshot
    assert snap, "publish stored an empty snapshot"
    assert snap["overview"]["product_info"]["product_name"]["value"] == "Snapshot Me"


def test_passport_edit_still_versions_once(auth_client):
    """A save that carries a passport must not double-snapshot just because
    it also flips status — the branches are mutually exclusive."""
    client, user = auth_client
    pid = _seed_draft(user["company_id"], "Edit And Publish")

    new_passport = {"overview": {"product_info": {"product_name": {"value": "Edited"}}}}
    r = client.patch(f"/api/products/{pid}", json={
        "passport": new_passport, "status": "published",
    })
    assert r.status_code == 200, r.text

    versions = client.get(f"/api/products/{pid}/versions").json()
    assert len(versions) == 1, "edit+publish in one request double-snapshotted"


def test_status_change_other_than_published_does_not_version(auth_client):
    """Archiving is not republishing."""
    client, user = auth_client
    pid = _seed_draft(user["company_id"], "Archive Me")

    client.patch(f"/api/products/{pid}", json={"status": "archived"})
    assert client.get(f"/api/products/{pid}/versions").json() == []


def test_rename_alone_does_not_version(auth_client):
    client, user = auth_client
    pid = _seed_draft(user["company_id"], "Rename Me")

    client.patch(f"/api/products/{pid}", json={"name": "New Name"})
    assert client.get(f"/api/products/{pid}/versions").json() == []
