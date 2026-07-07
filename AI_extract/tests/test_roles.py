"""Role gate: viewer can read, editor can edit, only admin can delete."""

from fastapi.testclient import TestClient
import api as api_module


def _seed_product(company_id: str) -> str:
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    with session_scope() as db:
        p = repo.create_product(db, passport={}, completeness=0.0,
                                source_documents=[], company_id=company_id)
        return p.id


def _make_user(company_id: str, email: str, role: str,
               password: str = "supersecretpass1") -> None:
    from dpp_extractor.db import session_scope
    from dpp_extractor.db import repository as repo
    from dpp_extractor import auth as auth_mod
    with session_scope() as db:
        repo.create_user(db, company_id=company_id, email=email,
                         password_hash=auth_mod.hash_password(password),
                         role=role)


def _login(client: TestClient, email: str,
           password: str = "supersecretpass1") -> None:
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text


def test_viewer_cannot_patch_product(register):
    admin_client = TestClient(api_module.app)
    _, admin = register(admin_client, email="admin_r1@co.example")
    pid = _seed_product(admin["company_id"])

    _make_user(admin["company_id"], "viewer1@co.example", role="viewer")
    viewer = TestClient(api_module.app)
    _login(viewer, "viewer1@co.example")

    r = viewer.patch(f"/api/products/{pid}", json={"name": "renamed"})
    assert r.status_code == 403


def test_viewer_cannot_delete_product(register):
    admin_client = TestClient(api_module.app)
    _, admin = register(admin_client, email="admin_r2@co.example")
    pid = _seed_product(admin["company_id"])

    _make_user(admin["company_id"], "viewer2@co.example", role="viewer")
    viewer = TestClient(api_module.app)
    _login(viewer, "viewer2@co.example")

    assert viewer.delete(f"/api/products/{pid}").status_code == 403


def test_viewer_can_read_product(register):
    admin_client = TestClient(api_module.app)
    _, admin = register(admin_client, email="admin_r3@co.example")
    pid = _seed_product(admin["company_id"])

    _make_user(admin["company_id"], "viewer3@co.example", role="viewer")
    viewer = TestClient(api_module.app)
    _login(viewer, "viewer3@co.example")

    assert viewer.get(f"/api/products/{pid}").status_code == 200
    assert viewer.get("/api/products").status_code == 200


def test_editor_can_patch_but_cannot_delete(register):
    admin_client = TestClient(api_module.app)
    _, admin = register(admin_client, email="admin_r4@co.example")
    pid = _seed_product(admin["company_id"])

    _make_user(admin["company_id"], "editor1@co.example", role="editor")
    editor = TestClient(api_module.app)
    _login(editor, "editor1@co.example")

    assert editor.patch(f"/api/products/{pid}", json={"name": "edited"}).status_code == 200
    assert editor.delete(f"/api/products/{pid}").status_code == 403


def test_admin_can_delete(register):
    admin_client = TestClient(api_module.app)
    _, admin = register(admin_client, email="admin_r5@co.example")
    pid = _seed_product(admin["company_id"])

    assert admin_client.delete(f"/api/products/{pid}").status_code == 200
    assert admin_client.get(f"/api/products/{pid}").status_code == 404


def test_only_admin_can_update_company(register):
    admin_client = TestClient(api_module.app)
    _, admin = register(admin_client, email="admin_r6@co.example")

    _make_user(admin["company_id"], "editor_c@co.example", role="editor")
    editor = TestClient(api_module.app)
    _login(editor, "editor_c@co.example")

    assert editor.patch("/api/company", json={"name": "Hijacked"}).status_code == 403
    r = admin_client.patch("/api/company", json={"name": "RealName Co"})
    assert r.status_code == 200
    assert r.json()["name"] == "RealName Co"
