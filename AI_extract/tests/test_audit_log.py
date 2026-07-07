"""H2 — admin actions land in the audit_log, scoped per company."""

from fastapi.testclient import TestClient
import api as api_module


def _seed(company_id: str) -> str:
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    with session_scope() as db:
        p = repo.create_product(db, passport={}, completeness=0.0,
                                source_documents=[], company_id=company_id)
        return p.id


def test_delete_product_writes_audit_entry(register):
    client = TestClient(api_module.app)
    _, admin = register(client, email="al_admin1@co.example", company="Audit Co 1")
    pid = _seed(admin["company_id"])
    assert client.delete(f"/api/products/{pid}").status_code == 200

    log = client.get("/api/audit-log").json()
    entry = next((e for e in log if e["action"] == "product.delete" and e["target_id"] == pid), None)
    assert entry is not None
    assert entry["actor_email"] == "al_admin1@co.example"


def test_company_update_writes_audit_entry(register):
    client = TestClient(api_module.app)
    register(client, email="al_admin2@co.example", company="Audit Co 2")
    assert client.patch("/api/company", json={"name": "Renamed Co"}).status_code == 200

    log = client.get("/api/audit-log").json()
    entry = next((e for e in log if e["action"] == "company.update"), None)
    assert entry is not None
    assert "name" in (entry["detail"] or {}).get("fields", [])


def test_audit_log_is_company_scoped(register):
    a = TestClient(api_module.app)
    _, ua = register(a, email="al_a@co.example", company="A")
    b = TestClient(api_module.app)
    _, ub = register(b, email="al_b@co.example", company="B")
    pid_a = _seed(ua["company_id"])
    a.delete(f"/api/products/{pid_a}")
    # B must NOT see A's audit entry.
    b_log = b.get("/api/audit-log").json()
    assert all(e["target_id"] != pid_a for e in b_log)


def test_audit_log_requires_admin(register):
    """Editor must NOT be able to read the audit log."""
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    from dpp_extractor import auth as auth_mod

    admin_client = TestClient(api_module.app)
    _, admin = register(admin_client, email="al_admin3@co.example", company="Audit Co 3")
    with session_scope() as db:
        repo.create_user(db, company_id=admin["company_id"],
                         email="al_editor@co.example",
                         password_hash=auth_mod.hash_password("supersecretpass1"),
                         role="editor")
    editor = TestClient(api_module.app)
    editor.post("/api/auth/login", json={
        "email": "al_editor@co.example", "password": "supersecretpass1"
    })
    assert editor.get("/api/audit-log").status_code == 403
