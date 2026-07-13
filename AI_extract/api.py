"""
FastAPI server for the DPP extraction pipeline.

Endpoints:
    POST /api/extract     — Upload files, start extraction, returns job_id
    GET  /api/jobs/{id}   — SSE stream of progress events + final result
"""

import asyncio
import json
import logging
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, UploadFile, File, Response, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

from dpp_extractor.pipeline.orchestrator import PipelineOrchestrator
from dpp_extractor.preprocessing.bom_parser import parse_bom_xlsx
from dpp_extractor.config import (
    UPLOADS_DIR, AUTH_COOKIE_NAME, COOKIE_SECURE, JWT_EXPIRE_HOURS,
    JWT_SECRET, JWT_SECRET_DEV_DEFAULT, IS_PRODUCTION, ENVIRONMENT,
    SIGNUP_ALLOWLIST,
)
from dpp_extractor.db import init_db, session_scope
from dpp_extractor.db import repository as repo
from dpp_extractor.db import models as db_models
from dpp_extractor import auth
from dpp_extractor.auth import get_current_user, require_role
from dpp_extractor.rate_limit import login_limiter, client_ip
from dpp_extractor import audit as audit_log
from dpp_extractor import assistant

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Files Gemini can process directly (sent as binary)
PDF_IMAGE_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".tif"}
# Files we parse ourselves and inject as structured context
BOM_EXTENSIONS = {".xlsx", ".xls"}
SUPPORTED_EXTENSIONS = PDF_IMAGE_EXTENSIONS | BOM_EXTENSIONS

app = FastAPI(title="DPP Extractor API", version="1.0.0")


# H3: security headers on every response. HSTS is only sent in production (it's
# annoying in dev because it forces https on localhost). CSP is permissive
# enough for the React SPA but blocks third-party script injection.
_SECURITY_HEADERS_BASE = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    ),
}


@app.middleware("http")
async def _security_headers(request, call_next):
    response = await call_next(request)
    for k, v in _SECURITY_HEADERS_BASE.items():
        response.headers.setdefault(k, v)
    if IS_PRODUCTION:
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )
    return response


# B6: sanitize unhandled exceptions in production so stack details don't reach
# clients. In dev mode we keep verbose output for debugging.
@app.exception_handler(Exception)
async def _unhandled_exception_handler(_request, exc):
    logger.exception("Unhandled exception")
    detail = "Internal server error" if IS_PRODUCTION else f"{type(exc).__name__}: {exc}"
    from fastapi.responses import JSONResponse
    return JSONResponse({"detail": detail}, status_code=500)

# In-memory job store for LIVE progress + SSE during a run. Completed jobs and
# their products are also persisted to the DB (so results survive restarts).
_jobs: dict[str, dict] = {}


# ── Request bodies ────────────────────────────────────────────────────────

class ProductUpdate(BaseModel):
    passport: Optional[dict] = None
    status: Optional[str] = None
    name: Optional[str] = None
    change_summary: Optional[str] = None   # version note when passport changes


class BatchCreate(BaseModel):
    lot: Optional[str] = None
    site: Optional[str] = None
    ref: Optional[str] = None
    production_date: Optional[str] = None
    notes: Optional[str] = None
    overrides: Optional[dict] = None


class ItemCreate(BaseModel):
    serial_number: Optional[str] = None
    dimensions: Optional[str] = None
    weight: Optional[str] = None
    destination: Optional[str] = None
    production_date: Optional[str] = None
    overrides: Optional[dict] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    vat: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class RegisterRequest(BaseModel):
    company_name: str
    email: str
    password: str
    name: Optional[str] = None


class ChatRequest(BaseModel):
    message: str


class LoginRequest(BaseModel):
    email: str
    password: str


@app.on_event("startup")
def _startup() -> None:
    """Initialize the database, seed the default company, and enforce
    production-hardened defaults (refuse to boot with insecure config in prod).
    """
    # --- B1: refuse to boot in production with the dev JWT secret -----------
    if IS_PRODUCTION and JWT_SECRET == JWT_SECRET_DEV_DEFAULT:
        raise RuntimeError(
            "Refusing to start: ENVIRONMENT=production but JWT_SECRET is still "
            "the insecure dev default. Set JWT_SECRET to a strong random value "
            "(e.g. `openssl rand -hex 32`) before deploying."
        )
    if IS_PRODUCTION and len(JWT_SECRET) < 32:
        raise RuntimeError(
            "Refusing to start: JWT_SECRET must be at least 32 characters in "
            "production. Generate one with `openssl rand -hex 32`."
        )
    # --- B5: warn loudly if cookies aren't secure in production -------------
    if IS_PRODUCTION and not COOKIE_SECURE:
        logger.warning(
            "COOKIE_SECURE is FALSE in production. Session cookies will leak "
            "over HTTP. Set COOKIE_SECURE=true and serve only over HTTPS."
        )
    if not IS_PRODUCTION and JWT_SECRET == JWT_SECRET_DEV_DEFAULT:
        logger.warning(
            f"Using insecure dev JWT_SECRET ({ENVIRONMENT} mode). "
            "Set JWT_SECRET and ENVIRONMENT=production before deploying."
        )
    init_db()
    with session_scope() as db:
        repo.get_or_create_default_company(db)


# ── Authentication ────────────────────────────────────────────────────────

def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=AUTH_COOKIE_NAME, value=token, httponly=True,
        samesite="lax", secure=COOKIE_SECURE,
        max_age=JWT_EXPIRE_HOURS * 3600, path="/",
    )


def _user_public(u) -> dict:
    return {"id": u.id, "company_id": u.company_id, "email": u.email,
            "name": u.name, "role": u.role}


@app.post("/api/auth/register")
async def register(body: RegisterRequest, response: Response):
    """Create a new company + its first admin user, and log them in."""
    if not body.email or not body.password:
        raise HTTPException(400, "Email and password are required")
    # Signup allowlist (private-beta gate): when configured, reject any email
    # not on the list. Empty allowlist = open registration (dev default).
    if SIGNUP_ALLOWLIST and body.email.strip().lower() not in SIGNUP_ALLOWLIST:
        raise HTTPException(
            403,
            "Registration is currently invite-only. Please contact the DeePPy team if you'd like access.",
        )
    if len(body.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    with session_scope() as db:
        if repo.get_user_by_email(db, body.email):
            raise HTTPException(409, "Email already registered")
        user = repo.create_company_with_admin(
            db, body.company_name, body.email,
            auth.hash_password(body.password), body.name,
        )
        uid, pub = user.id, _user_public(user)
    _set_auth_cookie(response, auth.create_access_token(uid))
    return {"user": pub}


@app.post("/api/auth/login")
async def login(body: LoginRequest, request: Request, response: Response):
    # H1: rate-limit by (IP, email) so brute force against one account from one
    # box stops at 5/min, but a real user typing the wrong password from a
    # different account doesn't get punished.
    key = f"login:{client_ip(request)}:{body.email.strip().lower()}"
    login_limiter.check(key)
    with session_scope() as db:
        user = repo.get_user_by_email(db, body.email)
        if not user or not auth.verify_password(body.password, user.password_hash):
            raise HTTPException(401, "Invalid email or password")
        if not user.is_active:
            raise HTTPException(403, "Account disabled")
        repo.touch_last_login(db, user.id)
        uid, pub = user.id, _user_public(user)
    _set_auth_cookie(response, auth.create_access_token(uid))
    return {"user": pub}


@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie(AUTH_COOKIE_NAME, path="/")
    return {"ok": True}


@app.get("/api/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return {"user": user}


# ── Health ────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    """Liveness + DB connectivity probe. Used by Docker healthcheck and any
    upstream load balancer. Returns 200 when the DB responds to SELECT 1."""
    from sqlalchemy import text
    from dpp_extractor.db.database import engine
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "environment": ENVIRONMENT}
    except Exception as e:
        logger.warning(f"Health probe failed: {type(e).__name__}: {e}")
        raise HTTPException(503, "Database unreachable")


# ── Serializers (must be called inside an open session) ───────────────────

def _product_summary(p) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "manufacturer": p.manufacturer_name,
        "family_code": p.family_code,
        "status": p.status,
        "completeness": p.completeness,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


def _item_detail(it) -> dict:
    return {
        "id": it.id, "batch_id": it.batch_id,
        "serial_number": it.serial_number, "dimensions": it.dimensions,
        "weight": it.weight, "destination": it.destination,
        "production_date": it.production_date, "overrides": it.overrides,
        "created_at": it.created_at.isoformat() if it.created_at else None,
    }


def _batch_detail(b) -> dict:
    return {
        "id": b.id, "product_id": b.product_id,
        "lot": b.lot, "site": b.site, "ref": b.ref,
        "production_date": b.production_date, "notes": b.notes,
        "overrides": b.overrides,
        "created_at": b.created_at.isoformat() if b.created_at else None,
        "items": [_item_detail(it) for it in b.items],
    }


def _company_dict(c) -> dict:
    return {
        "id": c.id, "name": c.name, "vat": c.vat, "address": c.address,
        "website": c.website, "email": c.email, "phone": c.phone,
    }


def _product_detail(p) -> dict:
    d = _product_summary(p)
    d["passport"] = p.passport
    stats = repo.compute_stats(p.passport or {})
    # Recall vs an attached expert "expected results" spec, if present.
    if p.eval_reference:
        from dpp_extractor import eval_recall
        stats["recall"] = eval_recall.compute_recall(p.passport or {}, p.eval_reference)
    d["stats"] = stats
    d["has_eval_reference"] = bool(p.eval_reference)
    d["source_documents"] = p.source_documents
    d["documents"] = [
        {"id": doc.id, "filename": doc.filename, "doc_type": doc.doc_type,
         "size_bytes": doc.size_bytes}
        for doc in p.documents
    ]
    d["batches"] = [_batch_detail(b) for b in p.batches]
    return d


@app.post("/api/extract")
async def extract(
    files: list[UploadFile] = File(default=[]),
    website_url: Optional[str] = Form(None),
    user: dict = Depends(require_role("admin", "editor")),
):
    """Accept document uploads + optional website URL, start async extraction, return job_id."""
    job_id = str(uuid.uuid4())[:8]

    # Save uploaded files to a temp directory; route by extension
    tmp_dir = Path(tempfile.mkdtemp(prefix="dpp_"))
    saved_paths: list[Path] = []          # PDFs/images sent to Gemini
    bom_paths: list[Path] = []            # BoM xlsx files (also persisted as Documents)
    bom_data_list: list[dict] = []        # Parsed BoM JSON dicts

    for f in files:
        ext = Path(f.filename).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            logger.warning(f"Skipping unsupported file: {f.filename}")
            continue
        dest = tmp_dir / f.filename
        dest.write_bytes(await f.read())

        if ext in BOM_EXTENSIONS:
            # Parse BoM xlsx into structured context for the extractor,
            # AND keep the file so it's persisted as a Document.
            parsed = parse_bom_xlsx(dest)
            if parsed:
                bom_data_list.append(parsed)
                bom_paths.append(dest)
                logger.info(f"Saved BoM: {f.filename} ({len(parsed.get('materials', []))} materials)")
            else:
                logger.warning(f"BoM parse returned empty for {f.filename}")
        else:
            saved_paths.append(dest)
            logger.info(f"Saved upload: {f.filename} ({dest.stat().st_size / 1024:.0f} KB)")

    if not saved_paths and not website_url and not bom_data_list:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return {"error": "No supported files or website URL provided", "job_id": None}

    # Normalize website URL
    clean_url = None
    if website_url and website_url.strip():
        clean_url = website_url.strip()
        if not clean_url.startswith("http"):
            clean_url = "https://" + clean_url
        logger.info(f"Website URL provided: {clean_url}")

    _jobs[job_id] = {
        "status": "queued",
        "step": None,
        "detail": None,
        "doc_index": 0,
        "doc_total": len(saved_paths),
        "progress": 0,
        "filenames": [p.name for p in saved_paths],
        "result": None,
        "error": None,
    }

    # Persist a job row so the run is tracked across restarts.
    with session_scope() as db:
        repo.create_job(db, job_id)

    asyncio.create_task(_run_pipeline(
        job_id, saved_paths, tmp_dir, website_url=clean_url,
        bom_data_list=bom_data_list, company_id=user["company_id"],
        bom_paths=bom_paths,
    ))
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
async def job_events(job_id: str, user: dict = Depends(get_current_user)):
    """SSE stream of job progress events (authenticated; cookie sent by EventSource)."""
    if job_id not in _jobs:
        return {"error": "Job not found"}

    async def stream():
        while True:
            job = _jobs.get(job_id)
            if not job:
                yield f"data: {json.dumps({'error': 'job disappeared'})}\n\n"
                break

            yield f"data: {json.dumps({k: v for k, v in job.items() if k != 'result'})}\n\n"

            if job["status"] in ("done", "error"):
                # Send final result as a separate event
                if job["result"]:
                    yield f"event: result\ndata: {json.dumps(job['result'], ensure_ascii=False)}\n\n"
                break

            await asyncio.sleep(1)

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/jobs/{job_id}/result")
async def job_result(job_id: str, user: dict = Depends(get_current_user)):
    """Get the final extraction result (poll after SSE signals done).

    Falls back to the DB when the job is no longer in memory (e.g. after a
    container restart), reconstructing the result from the persisted product.
    """
    job = _jobs.get(job_id)
    if job:
        if job["status"] != "done":
            return {"status": job["status"], "progress": job["progress"]}
        return job["result"]

    # Not in memory — look it up in the DB (scoped to the caller's company).
    with session_scope() as db:
        db_job = repo.get_job(db, job_id)
        if not db_job:
            return {"error": "Job not found"}
        if db_job.status != "done" or not db_job.product_id:
            return {"status": db_job.status, "error": db_job.error}
        product = repo.get_product(db, db_job.product_id)
        if not product or product.company_id != user["company_id"]:
            raise HTTPException(404, "Product not found")
        return {
            "passport": product.passport,
            "stats": db_job.stats,
            "product_id": product.id,
        }


# ---------------------------------------------------------------------------
# Product CRUD (read endpoints — P2; write/PATCH + batches/items land in P3)
# ---------------------------------------------------------------------------

def _owned_product(db, product_id: str, company_id: str):
    """Fetch a product only if it belongs to the caller's company, else None."""
    product = repo.get_product(db, product_id)
    if not product or product.company_id != company_id:
        return None
    return product


@app.get("/api/company")
async def get_company(user: dict = Depends(get_current_user)):
    """Get the caller's company profile."""
    with session_scope() as db:
        company = repo.get_company(db, user["company_id"])
        if not company:
            raise HTTPException(404, "Company not found")
        return _company_dict(company)


@app.get("/api/audit-log")
async def list_audit_log(user: dict = Depends(require_role("admin")),
                         limit: int = 200):
    """Recent admin actions for the caller's company (admin only)."""
    limit = max(1, min(1000, limit))
    with session_scope() as db:
        entries = audit_log.list_for_company(db, user["company_id"], limit=limit)
        return [
            {
                "id": e.id, "action": e.action,
                "actor_email": e.actor_email,
                "target_type": e.target_type, "target_id": e.target_id,
                "detail": e.detail, "ip": e.ip,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ]


@app.patch("/api/company")
async def update_company(body: CompanyUpdate, request: Request,
                         user: dict = Depends(require_role("admin"))):
    """Update the caller's company profile (admin only)."""
    changes = body.model_dump(exclude_none=True)
    with session_scope() as db:
        company = repo.update_company(db, user["company_id"], **changes)
        if not company:
            raise HTTPException(404, "Company not found")
        audit_log.record(
            db, action="company.update", actor=user,
            target_type="company", target_id=company.id,
            detail={"fields": sorted(changes.keys())},
            ip=client_ip(request),
        )
        return _company_dict(company)


@app.get("/api/products")
async def list_products(user: dict = Depends(get_current_user)):
    """List the caller's company products (summary view for the dashboard)."""
    with session_scope() as db:
        return [_product_summary(p) for p in repo.list_products(db, company_id=user["company_id"])]


def _unwrap(node):
    """Return the .value from a wrapped ExtractedField dict, or the node as-is."""
    if isinstance(node, dict) and "value" in node:
        return node["value"]
    return node


def _catalog_kpis(passport: dict) -> dict:
    """Pull the 3 catalog-card KPIs from a passport. Returns None per field
    when the data isn't there — the UI shows '—' for those.

      • gwp_total       — sum of lifecycle.stages[].gwp_total (typical EPD)
      • recycled        — performance.values row matching /recycl|riciclat/i
      • energy_class    — performance.energy_class (when present)
    """
    pp = passport or {}

    gwp_total = None
    stages = ((pp.get("lifecycle") or {}).get("stages")) or []
    if isinstance(stages, list):
        running = 0.0
        any_value = False
        for s in stages:
            if not isinstance(s, dict):
                continue
            try:
                running += float(_unwrap(s.get("gwp_total")))
                any_value = True
            except (TypeError, ValueError):
                continue
        if any_value:
            gwp_total = round(running, 2)

    recycled = None
    perf = pp.get("performance") or {}
    values = perf.get("values") or []
    if isinstance(values, list):
        for row in values:
            if not isinstance(row, dict):
                continue
            name = _unwrap(row.get("property_name")) or ""
            if not isinstance(name, str):
                continue
            low = name.lower()
            if "recycl" in low or "riciclat" in low:
                raw = _unwrap(row.get("value"))
                if raw not in (None, ""):
                    s = str(raw).strip()
                    if not s.endswith("%"):
                        s = f"{s}%"
                    recycled = s
                    break

    energy_class = _unwrap(perf.get("energy_class"))
    if isinstance(energy_class, str):
        energy_class = energy_class.strip() or None

    return {
        "gwp_total": gwp_total,
        "recycled": recycled,
        "energy_class": energy_class,
    }


@app.get("/api/catalog/{product_id}")
async def get_catalog_product(product_id: str, user: dict = Depends(get_current_user)):
    """Catalog detail: a single product, but only if it's published.

    Bypasses tenant scoping (catalog is cross-company by design) and
    returns the full passport so the public DPP overlay can render it.
    Drafts and archived products are not accessible through this path.
    """
    with session_scope() as db:
        product = repo.get_product(db, product_id)
        if not product or product.status != "published":
            raise HTTPException(404, "Product not found")
        return _product_detail(product)


@app.get("/api/catalog")
async def list_catalog(user: dict = Depends(get_current_user)):
    """Public catalog: every status='published' product across all companies.

    Intentionally cross-tenant. Each item carries `is_own=True` when the
    product belongs to the caller's company so the UI can badge it.
    No drafts and no other-company internals are exposed beyond the
    summary + 3 KPI fields below.
    """
    with session_scope() as db:
        rows = repo.list_products(db, status="published")
        # Resolve company display names in one query.
        company_ids = {p.company_id for p in rows if p.company_id}
        companies = {
            c.id: c.name
            for c in db.query(db_models.Company)
                       .filter(db_models.Company.id.in_(company_ids))
                       .all()
        } if company_ids else {}
        my_company = user["company_id"]
        return [
            {
                "id": p.id,
                "name": p.name,
                "manufacturer": p.manufacturer_name or companies.get(p.company_id),
                "family_code": p.family_code,
                "company_id": p.company_id,
                "company_name": companies.get(p.company_id),
                "is_own": p.company_id == my_company,
                "kpis": _catalog_kpis(p.passport or {}),
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in rows
        ]


@app.get("/api/products/{product_id}")
async def get_product(product_id: str, user: dict = Depends(get_current_user)):
    """Get a single product (only if it belongs to the caller's company)."""
    with session_scope() as db:
        product = _owned_product(db, product_id, user["company_id"])
        if not product:
            raise HTTPException(404, "Product not found")
        return _product_detail(product)


@app.get("/api/products/{product_id}/documents/{doc_id}")
async def get_document_file(product_id: str, doc_id: str,
                            user: dict = Depends(get_current_user)):
    """Stream an uploaded source file (PDF, image, BoM) back to the client.
    Used by the UI to render product images and offer document downloads."""
    with session_scope() as db:
        if not _owned_product(db, product_id, user["company_id"]):
            raise HTTPException(404, "Product not found")
        doc = db.get(db_models.Document, doc_id)
        if not doc or doc.product_id != product_id:
            raise HTTPException(404, "Document not found")
        if not doc.storage_path:
            raise HTTPException(404, "File not stored on disk")
        # B2: harden against path traversal — resolve the canonical path and
        # ensure it lives under the uploads volume. A row whose storage_path
        # has been tampered with (or a future bug) can't read /etc/passwd.
        try:
            resolved = Path(doc.storage_path).resolve(strict=False)
            uploads_root = UPLOADS_DIR.resolve(strict=False)
            resolved.relative_to(uploads_root)
        except (ValueError, OSError):
            logger.warning(
                f"Rejected document fetch outside uploads volume: "
                f"product={product_id} doc={doc_id} path={doc.storage_path}"
            )
            raise HTTPException(404, "Document not found")
        if not resolved.exists():
            raise HTTPException(404, "File missing from disk")
        return FileResponse(str(resolved), filename=doc.filename)


@app.post("/api/products/{product_id}/eval-reference")
async def upload_eval_reference(product_id: str, file: UploadFile = File(...),
                                user: dict = Depends(require_role("admin", "editor"))):
    """Attach an expert 'expected results' XLSX → enables recall-vs-ground-truth scoring."""
    from dpp_extractor import eval_recall
    tmp = Path(tempfile.mkdtemp(prefix="eval_")) / (file.filename or "expected.xlsx")
    tmp.write_bytes(await file.read())
    try:
        rows = eval_recall.parse_expected_xlsx(tmp)
    except Exception:
        # Log the real exception server-side; return a generic message to the
        # client so we don't leak stack details (B6).
        logger.exception(f"Failed to parse expected-results upload: {file.filename}")
        shutil.rmtree(tmp.parent, ignore_errors=True)
        raise HTTPException(400, "Could not parse expected-results file. Check that it is a valid .xlsx in the ontology format.")
    finally:
        shutil.rmtree(tmp.parent, ignore_errors=True)
    if not rows:
        raise HTTPException(400, "No expected values found in the file (check the 'Dato output' column).")
    with session_scope() as db:
        if not _owned_product(db, product_id, user["company_id"]):
            raise HTTPException(404, "Product not found")
        product = repo.set_eval_reference(db, product_id, rows)
        recall = eval_recall.compute_recall(product.passport or {}, rows)
        return {"expected_fields": len(rows), "recall": recall}


@app.patch("/api/products/{product_id}")
async def update_product(product_id: str, body: ProductUpdate,
                         user: dict = Depends(require_role("admin", "editor"))):
    """Save edits to a product (editor/admin). Snapshots a version on passport change."""
    with session_scope() as db:
        product = _owned_product(db, product_id, user["company_id"])
        if not product:
            raise HTTPException(404, "Product not found")

        if body.passport is not None:
            repo.update_product_passport(db, product_id, body.passport)
            n = repo.count_versions(db, product_id) + 1
            repo.create_version(
                db, product_id,
                passport_snapshot=body.passport,
                label=f"v{n}",
                change_summary=body.change_summary,
            )
        if body.status is not None or body.name is not None:
            repo.update_product_fields(db, product_id, status=body.status, name=body.name)

        db.flush()
        return _product_detail(product)


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str, request: Request,
                         user: dict = Depends(require_role("admin"))):
    """Delete a product and its hierarchy (admin only, own company)."""
    with session_scope() as db:
        product = _owned_product(db, product_id, user["company_id"])
        if not product:
            raise HTTPException(404, "Product not found")
        snapshot = {"name": product.name, "family_code": product.family_code,
                    "manufacturer": product.manufacturer_name}
        repo.delete_product(db, product_id)
        audit_log.record(
            db, action="product.delete", actor=user,
            target_type="product", target_id=product_id,
            detail=snapshot, ip=client_ip(request),
        )
        return {"deleted": True}


@app.get("/api/products/{product_id}/versions")
async def list_versions(product_id: str, user: dict = Depends(get_current_user)):
    """Version history for a product (own company)."""
    with session_scope() as db:
        if not _owned_product(db, product_id, user["company_id"]):
            raise HTTPException(404, "Product not found")
        return [
            {"id": v.id, "label": v.label, "change_summary": v.change_summary,
             "created_at": v.created_at.isoformat() if v.created_at else None}
            for v in repo.list_versions(db, product_id)
        ]


def _messages_to_thread(blob) -> list[dict]:
    """Render serialized pydantic-ai messages into a simple UI thread."""
    thread = []
    for msg in (blob or []):
        for part in (msg.get("parts") or []):
            kind = part.get("part_kind")
            if kind == "user-prompt":
                c = part.get("content")
                thread.append({"from": "user", "text": c if isinstance(c, str) else str(c)})
            elif kind == "text":
                txt = part.get("content")
                if txt:
                    thread.append({"from": "agent", "text": txt})
    return thread


@app.get("/api/products/{product_id}/chat")
async def get_chat(product_id: str, user: dict = Depends(get_current_user)):
    """Load the user's conversation thread for this product."""
    with session_scope() as db:
        if not _owned_product(db, product_id, user["company_id"]):
            raise HTTPException(404, "Product not found")
        conv = repo.get_or_create_conversation(db, product_id, user["company_id"], user["id"])
        return {
            "conversation_id": conv.id,
            "messages": _messages_to_thread(conv.messages),
            "available": assistant.assistant_available(),
        }


@app.post("/api/products/{product_id}/chat/new")
async def new_chat(product_id: str, user: dict = Depends(get_current_user)):
    """Start a fresh conversation thread (the old one is kept in the DB)."""
    with session_scope() as db:
        if not _owned_product(db, product_id, user["company_id"]):
            raise HTTPException(404, "Product not found")
        conv = repo.create_conversation(db, product_id, user["company_id"], user["id"])
        return {"conversation_id": conv.id, "messages": [], "available": assistant.assistant_available()}


@app.post("/api/products/{product_id}/chat")
async def post_chat(product_id: str, body: ChatRequest, user: dict = Depends(get_current_user)):
    """Send a message to the product assistant (stateless: load history → run → save)."""
    if not assistant.assistant_available():
        raise HTTPException(503, "Assistant not configured (missing OPENAI_API_KEY)")
    if not body.message or not body.message.strip():
        raise HTTPException(400, "Empty message")

    from pydantic_ai.messages import ModelMessagesTypeAdapter

    # Load product + conversation under a session, then release it before the LLM call.
    with session_scope() as db:
        product = _owned_product(db, product_id, user["company_id"])
        if not product:
            raise HTTPException(404, "Product not found")
        passport = product.passport or {}
        product_name = product.name
        conv = repo.get_or_create_conversation(db, product_id, user["company_id"], user["id"])
        conv_id = conv.id
        history_blob = conv.messages or []

    try:
        history = ModelMessagesTypeAdapter.validate_python(history_blob) if history_blob else None
    except Exception:
        logger.warning("Could not deserialize chat history; starting fresh")
        history = None

    deps = assistant.ProductChatDeps(passport=passport, product_name=product_name)
    result = await assistant.get_agent().run(body.message, message_history=history, deps=deps)

    new_blob = ModelMessagesTypeAdapter.dump_python(result.all_messages(), mode="json")
    with session_scope() as db:
        repo.save_conversation_messages(db, conv_id, new_blob)

    return {"conversation_id": conv_id, "reply": result.output}


@app.post("/api/products/{product_id}/batches")
async def create_batch(product_id: str, body: BatchCreate,
                       user: dict = Depends(require_role("admin", "editor"))):
    """Create a production batch (Project DPP) under a product (editor/admin)."""
    with session_scope() as db:
        if not _owned_product(db, product_id, user["company_id"]):
            raise HTTPException(404, "Product not found")
        batch = repo.create_batch(
            db, product_id,
            lot=body.lot, site=body.site, ref=body.ref,
            production_date=body.production_date, notes=body.notes,
            overrides=body.overrides or {},
        )
        return _batch_detail(batch)


@app.post("/api/batches/{batch_id}/items")
async def create_item(batch_id: str, body: ItemCreate,
                      user: dict = Depends(require_role("admin", "editor"))):
    """Create an individual item under a batch (editor/admin, own company)."""
    with session_scope() as db:
        batch = repo.get_batch(db, batch_id)
        if not batch or not _owned_product(db, batch.product_id, user["company_id"]):
            raise HTTPException(404, "Batch not found")
        item = repo.create_item(
            db, batch_id,
            serial_number=body.serial_number, dimensions=body.dimensions,
            weight=body.weight, destination=body.destination,
            production_date=body.production_date, overrides=body.overrides or {},
        )
        return _item_detail(item)


# ---------------------------------------------------------------------------
# Background pipeline runner
# ---------------------------------------------------------------------------

async def _run_pipeline(
    job_id: str,
    file_paths: list[Path],
    tmp_dir: Path,
    website_url: Optional[str] = None,
    bom_data_list: Optional[list[dict]] = None,
    company_id: Optional[str] = None,
    bom_paths: Optional[list[Path]] = None,
):
    """Run the 3-pass pipeline and update job state with progress."""
    job = _jobs[job_id]

    def on_progress(step: str, doc_index: int = 0, doc_total: int = 0, detail: str = ""):
        job["step"] = step
        job["doc_index"] = doc_index
        job["doc_total"] = doc_total
        job["detail"] = detail

        # Calculate overall progress %
        if step == "classify":
            job["progress"] = int(10 + (doc_index / max(doc_total, 1)) * 30)
        elif step == "extract":
            job["progress"] = int(40 + (doc_index / max(doc_total, 1)) * 45)
        elif step == "merge":
            job["progress"] = 90
        elif step == "done":
            job["progress"] = 100

    try:
        job["status"] = "running"
        job["progress"] = 5

        orchestrator = PipelineOrchestrator()
        passport, merge_result = await orchestrator.process(
            file_paths,
            on_progress=on_progress,
            website_url=website_url,
            bom_data_list=bom_data_list or [],
        )

        on_progress("done")
        passport_dict = passport.to_frontend_dict()
        # Use the canonical required-based stats so extraction-time numbers
        # match what the reload/edit path computes; add merge-only extras.
        stats = {
            **repo.compute_stats(passport_dict),
            "documents_processed": len(merge_result.documents_merged),
            "conflicts_resolved": len(merge_result.conflicts),
        }
        result = {"passport": passport_dict, "stats": stats}

        # Persist: create the product, copy uploaded files, link documents,
        # and finalize the job — all so results survive a container restart.
        try:
            product_id = _persist_extraction(job_id, passport_dict, stats, file_paths, company_id, bom_paths)
            result["product_id"] = product_id
        except Exception:
            logger.exception(f"Failed to persist extraction for job {job_id}")

        job["status"] = "done"
        job["result"] = result

    except Exception as e:
        logger.exception(f"Pipeline failed for job {job_id}")
        job["status"] = "error"
        job["error"] = str(e)
        try:
            with session_scope() as db:
                repo.finish_job(db, job_id, status="error", error=str(e))
        except Exception:
            logger.exception(f"Failed to persist job error for {job_id}")

    finally:
        # Cleanup temp files
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _persist_extraction(
    job_id: str, passport_dict: dict, stats: dict, file_paths: list[Path],
    company_id: Optional[str] = None, bom_paths: Optional[list[Path]] = None,
) -> str:
    """Create the product + documents, copy uploads, finalize the job.

    Returns the new product id. The product is assigned to the extracting
    user's company (falls back to the default company if none provided).
    Both PDFs and BoM xlsx files are persisted as Documents so the user can
    see every source file that contributed to the extraction.
    """
    with session_scope() as db:
        cid = company_id or repo.get_or_create_default_company(db).id
        source_docs = (passport_dict.get("metadata") or {}).get("source_documents", [])
        product = repo.create_product(
            db,
            passport=passport_dict,
            completeness=stats.get("completeness", 0.0),
            source_documents=source_docs,
            company_id=cid,
        )
        product_id = product.id

        # Copy uploaded source files (PDFs + BoMs) into the persistent uploads
        # volume and persist as Document rows.
        dest_dir = UPLOADS_DIR / product_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        for fp in file_paths:
            try:
                target = dest_dir / fp.name
                shutil.copy2(fp, target)
                repo.add_document(
                    db,
                    product_id,
                    filename=fp.name,
                    storage_path=str(target),
                    size_bytes=target.stat().st_size,
                )
            except Exception:
                logger.warning(f"Could not persist upload {fp.name}")
        for fp in (bom_paths or []):
            try:
                target = dest_dir / fp.name
                shutil.copy2(fp, target)
                repo.add_document(
                    db,
                    product_id,
                    filename=fp.name,
                    doc_type="BoM",
                    storage_path=str(target),
                    size_bytes=target.stat().st_size,
                )
            except Exception:
                logger.warning(f"Could not persist BoM {fp.name}")

        # If the user uploaded an image, surface it as the product image in
        # the passport (only if the AI didn't already set one).
        _IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".tif"}
        images = [fp for fp in file_paths if fp.suffix.lower() in _IMG_EXTS]
        if images:
            pi = passport_dict.setdefault("overview", {}).setdefault("product_info", {})
            current = pi.get("product_image")
            already_set = isinstance(current, dict) and current.get("value")
            if not already_set:
                pi["product_image"] = {
                    "value": images[0].name,
                    "confidence": "high",
                    "source": {"document_name": images[0].name, "document_type": None,
                               "source_family": None, "page": None, "snippet": None},
                    "note": "Uploaded as product image",
                }
                repo.update_product_passport(db, product_id, passport_dict)

        repo.finish_job(db, job_id, status="done", product_id=product_id, stats=stats)
        return product_id
