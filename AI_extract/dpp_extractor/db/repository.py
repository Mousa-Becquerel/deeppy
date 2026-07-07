"""
Repository helpers — thin CRUD over the ORM models.

Keeps SQLAlchemy specifics out of api.py and centralizes the logic for
deriving 'hot' columns from the passport JSON.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from . import models

# Default company seeded on first boot (until auth/multi-tenant lands).
_DEFAULT_COMPANY = {
    "name": "Levery S.r.l. Società Benefit",
    "vat": "IT04730050400",
    "address": "Via Pisino 66, 47814 Bellaria Igea Marina (RN), Italy",
    "website": "https://levery.it",
    "email": "info@levery.it",
    "phone": "",
}


# ── Hot-column extraction from passport JSON ──────────────────────────────

def _ef_value(passport: dict, *path: str) -> Optional[str]:
    """Read a nested ExtractedField's .value via a dotted path. Safe on missing."""
    obj = passport or {}
    for key in path:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
        if obj is None:
            return None
    if isinstance(obj, dict):
        return obj.get("value")
    return obj


def derive_hot_columns(passport: dict) -> dict:
    """Pull the denormalized list/search columns out of a passport dict."""
    name = _ef_value(passport, "overview", "product_info", "product_name")
    mfr = _ef_value(passport, "overview", "manufacturer", "company_name")
    family_code = _ef_value(passport, "overview", "product_info", "product_family_code")
    if not family_code:
        # Fall back to metadata.product_family (full name) if code missing
        family_code = (passport.get("metadata") or {}).get("product_family")
    return {
        "name": name or "Untitled Product",
        "manufacturer_name": mfr,
        "family_code": family_code,
    }


# Mandatory fields per ontology Data_ontology (Required/Optional column).
# Completion rate is measured against THESE, not every possible field.
REQUIRED_FIELDS: list[tuple[str, str]] = [
    ("overview.product_info.product_name", "Product name"),
    ("overview.product_info.uid", "UID"),
    ("overview.product_info.item_type", "Item type"),
    ("overview.product_info.product_family", "Product family"),
    ("overview.product_info.intended_use", "Intended use"),
    ("overview.product_info.functional_unit", "Functional unit"),
    ("overview.product_info.production_period", "Production period"),
    ("overview.manufacturer.company_name", "Company name"),
    ("overview.manufacturer.address", "Address"),
    ("overview.manufacturer.website", "Website"),
    ("overview.manufacturer.manufacturing_site", "Manufacturing site"),
    ("overview.manufacturer.email", "Email"),
]


def _path_value(passport: dict, dotted: str):
    """Read a nested ExtractedField's .value via a dotted path. Safe on missing."""
    obj = passport or {}
    for key in dotted.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
        if obj is None:
            return None
    return obj.get("value") if isinstance(obj, dict) else obj


def _is_empty(v) -> bool:
    return v in (None, "", [], {})


def compute_required(passport: dict) -> tuple[int, int, list[str]]:
    """Return (filled, total, missing_labels) over the mandatory fields only."""
    filled = 0
    missing: list[str] = []

    for path, label in REQUIRED_FIELDS:
        v = _path_value(passport, path)
        # product_family may be present only as the code variant
        if _is_empty(v) and path == "overview.product_info.product_family":
            v = _path_value(passport, "overview.product_info.product_family_code")
        if not _is_empty(v):
            filled += 1
        else:
            missing.append(label)

    # Composition: at least one bill-of-materials entry (Product #1 is Required)
    mats = ((passport or {}).get("composition") or {}).get("materials") or []
    def _mat_desc(m):
        dsc = m.get("description") if isinstance(m, dict) else None
        return dsc.get("value") if isinstance(dsc, dict) else dsc
    if any(not _is_empty(_mat_desc(m)) for m in mats):
        filled += 1
    else:
        missing.append("Bill of materials (≥1 product)")

    total = len(REQUIRED_FIELDS) + 1  # + the composition requirement
    return filled, total, missing


def compute_completeness(passport: dict) -> float:
    """Completion rate = mandatory fields filled / mandatory fields total."""
    filled, total, _ = compute_required(passport)
    return round(filled / total * 100, 1) if total else 0.0


def compute_stats(passport: dict) -> dict:
    """Stats block: required-based completeness + overall confidence counts.

    - completeness / required_*  → measured over mandatory fields only
    - confidence / *_fields      → overall distribution across all fields
      (drives the 'auto / to review / missing' badges)
    Always recomputed from the passport, so it stays correct after edits.
    """
    high = med = low = filled = total = 0

    def walk(obj):
        nonlocal high, med, low, filled, total
        if isinstance(obj, dict):
            if "confidence" in obj and "value" in obj:
                total += 1
                if obj.get("value") not in (None, "", [], {}):
                    filled += 1
                c = obj.get("confidence")
                if c == "high":
                    high += 1
                elif c == "medium":
                    med += 1
                else:
                    low += 1
                return
            for val in obj.values():
                walk(val)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    for section in ("overview", "composition", "performance", "compliance", "lifecycle"):
        walk((passport or {}).get(section))

    req_filled, req_total, missing_required = compute_required(passport)
    return {
        # Headline = mandatory-fields completion (per ontology Required set)
        "completeness": round(req_filled / req_total * 100, 1) if req_total else 0.0,
        "required_filled": req_filled,
        "required_total": req_total,
        "missing_required": missing_required,
        # All-fields completion (mandatory + optional)
        "overall_completeness": round(filled / total * 100, 1) if total else 0.0,
        "fields_filled": filled,
        "total_fields": total,
        "confidence": {"high": high, "medium": med, "low": low},
    }


# ── Company ───────────────────────────────────────────────────────────────

def get_or_create_default_company(db: Session) -> models.Company:
    company = db.scalars(select(models.Company)).first()
    if company:
        return company
    company = models.Company(**_DEFAULT_COMPANY)
    db.add(company)
    db.flush()
    return company


# ── Users ─────────────────────────────────────────────────────────────────

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.scalars(
        select(models.User).where(models.User.email == email.strip().lower())
    ).first()


def get_user(db: Session, user_id: str) -> Optional[models.User]:
    return db.get(models.User, user_id)


def create_company_with_admin(
    db: Session, company_name: str, email: str, password_hash: str, name: Optional[str] = None
) -> models.User:
    """Register flow: create a new company and its first admin user."""
    company = models.Company(name=company_name or "My Company")
    db.add(company)
    db.flush()
    user = models.User(
        company_id=company.id,
        email=email.strip().lower(),
        password_hash=password_hash,
        name=name,
        role="admin",
    )
    db.add(user)
    db.flush()
    return user


def create_user(
    db: Session, company_id: str, email: str, password_hash: str,
    name: Optional[str] = None, role: str = "editor",
) -> models.User:
    user = models.User(
        company_id=company_id, email=email.strip().lower(),
        password_hash=password_hash, name=name, role=role,
    )
    db.add(user)
    db.flush()
    return user


def touch_last_login(db: Session, user_id: str) -> None:
    user = db.get(models.User, user_id)
    if user:
        user.last_login = datetime.now(timezone.utc)
        db.flush()


_COMPANY_FIELDS = ("name", "vat", "address", "website", "email", "phone")


def get_company(db: Session, company_id: str) -> Optional[models.Company]:
    return db.get(models.Company, company_id)


def update_company(db: Session, company_id: str, **fields) -> Optional[models.Company]:
    """Update a company by id with the provided fields."""
    company = db.get(models.Company, company_id)
    if not company:
        return None
    for key, value in fields.items():
        if key in _COMPANY_FIELDS and value is not None:
            setattr(company, key, value)
    db.flush()
    return company


# ── Product ─────────────────────────────────────────────────────────────--

def create_product(
    db: Session,
    passport: dict,
    completeness: float,
    source_documents: list[str],
    company_id: Optional[str] = None,
    status: str = "draft",
) -> models.Product:
    hot = derive_hot_columns(passport)
    product = models.Product(
        company_id=company_id,
        status=status,
        completeness=round(completeness or 0.0, 1),
        passport=passport,
        source_documents=source_documents or [],
        **hot,
    )
    db.add(product)
    db.flush()
    return product


def list_products(
    db: Session,
    company_id: Optional[str] = None,
    status: Optional[str] = None,
) -> list[models.Product]:
    stmt = select(models.Product).order_by(models.Product.created_at.desc())
    if company_id:
        stmt = stmt.where(models.Product.company_id == company_id)
    if status:
        stmt = stmt.where(models.Product.status == status)
    return list(db.scalars(stmt))


def get_product(db: Session, product_id: str) -> Optional[models.Product]:
    return db.get(models.Product, product_id)


def update_product_passport(
    db: Session, product_id: str, passport: dict, completeness: Optional[float] = None
) -> Optional[models.Product]:
    product = db.get(models.Product, product_id)
    if not product:
        return None
    product.passport = passport
    # Force-flag the JSON column as dirty. SQLAlchemy's plain JSON type does
    # NOT auto-detect in-place mutations (or same-identity reassignment), so
    # without this the passport edit silently no-ops on flush.
    flag_modified(product, "passport")
    hot = derive_hot_columns(passport)
    product.name = hot["name"]
    product.manufacturer_name = hot["manufacturer_name"]
    product.family_code = hot["family_code"]
    product.completeness = (
        round(completeness, 1) if completeness is not None
        else compute_completeness(passport)
    )
    db.flush()
    return product


def update_product_fields(
    db: Session,
    product_id: str,
    status: Optional[str] = None,
    name: Optional[str] = None,
) -> Optional[models.Product]:
    """Update simple product attributes (status, name) without touching passport."""
    product = db.get(models.Product, product_id)
    if not product:
        return None
    if status is not None:
        product.status = status
    if name is not None:
        product.name = name
    db.flush()
    return product


def set_eval_reference(db: Session, product_id: str, rows: list) -> Optional[models.Product]:
    """Attach an expert 'expected results' spec for recall scoring."""
    product = db.get(models.Product, product_id)
    if not product:
        return None
    product.eval_reference = rows
    db.flush()
    return product


def delete_product(db: Session, product_id: str) -> bool:
    product = db.get(models.Product, product_id)
    if not product:
        return False
    # extraction_jobs.product_id is a nullable FK without cascade, so SQLite
    # raises "FOREIGN KEY constraint failed" on delete unless we detach the
    # job rows first. We keep the jobs (audit trail of what was run) but
    # null out the dangling product reference.
    db.query(models.ExtractionJob)\
      .filter(models.ExtractionJob.product_id == product_id)\
      .update({"product_id": None}, synchronize_session=False)
    db.delete(product)  # cascades to batches/items/documents/versions
    db.flush()
    return True


# ── Documents ──────────────────────────────────────────────────────────--

def add_document(
    db: Session,
    product_id: str,
    filename: str,
    doc_type: Optional[str] = None,
    family: Optional[str] = None,
    storage_path: Optional[str] = None,
    size_bytes: Optional[int] = None,
) -> models.Document:
    doc = models.Document(
        product_id=product_id,
        filename=filename,
        doc_type=doc_type,
        family=family,
        storage_path=storage_path,
        size_bytes=size_bytes,
    )
    db.add(doc)
    db.flush()
    return doc


# ── Extraction jobs ───────────────────────────────────────────────────────

def create_job(db: Session, job_id: str) -> models.ExtractionJob:
    job = models.ExtractionJob(id=job_id, status="queued", progress=0)
    db.add(job)
    db.flush()
    return job


def finish_job(
    db: Session,
    job_id: str,
    status: str,
    product_id: Optional[str] = None,
    stats: Optional[dict] = None,
    error: Optional[str] = None,
) -> Optional[models.ExtractionJob]:
    job = db.get(models.ExtractionJob, job_id)
    if not job:
        job = models.ExtractionJob(id=job_id)
        db.add(job)
    job.status = status
    job.progress = 100 if status == "done" else job.progress
    job.product_id = product_id
    job.stats = stats
    job.error = error
    job.completed_at = datetime.now(timezone.utc)
    db.flush()
    return job


def get_job(db: Session, job_id: str) -> Optional[models.ExtractionJob]:
    return db.get(models.ExtractionJob, job_id)


# ── Batches & Items ───────────────────────────────────────────────────────

def create_batch(db: Session, product_id: str, **fields) -> models.Batch:
    batch = models.Batch(product_id=product_id, **fields)
    db.add(batch)
    db.flush()
    return batch


def get_batch(db: Session, batch_id: str) -> Optional[models.Batch]:
    return db.get(models.Batch, batch_id)


def create_item(db: Session, batch_id: str, **fields) -> models.Item:
    item = models.Item(batch_id=batch_id, **fields)
    db.add(item)
    db.flush()
    return item


# ── Versions ───────────────────────────────────────────────────────────--

def create_version(
    db: Session,
    product_id: str,
    passport_snapshot: dict,
    label: Optional[str] = None,
    change_summary: Optional[str] = None,
) -> models.Version:
    version = models.Version(
        product_id=product_id,
        label=label,
        change_summary=change_summary,
        passport_snapshot=passport_snapshot,
    )
    db.add(version)
    db.flush()
    return version


def get_or_create_conversation(
    db: Session, product_id: str, company_id: str, user_id: str
) -> models.Conversation:
    """Return the user's rolling conversation for this product, creating it if absent."""
    conv = db.scalars(
        select(models.Conversation)
        .where(models.Conversation.product_id == product_id)
        .where(models.Conversation.user_id == user_id)
        .order_by(models.Conversation.created_at.desc())
    ).first()
    if conv:
        return conv
    conv = models.Conversation(
        product_id=product_id, company_id=company_id, user_id=user_id, messages=[]
    )
    db.add(conv)
    db.flush()
    return conv


def create_conversation(
    db: Session, product_id: str, company_id: str, user_id: str
) -> models.Conversation:
    """Always start a fresh conversation (used by 'New chat')."""
    conv = models.Conversation(
        product_id=product_id, company_id=company_id, user_id=user_id, messages=[]
    )
    db.add(conv)
    db.flush()
    return conv


def save_conversation_messages(db: Session, conversation_id: str, messages: list) -> None:
    conv = db.get(models.Conversation, conversation_id)
    if conv:
        conv.messages = messages
        db.flush()


def list_versions(db: Session, product_id: str) -> list[models.Version]:
    stmt = (
        select(models.Version)
        .where(models.Version.product_id == product_id)
        .order_by(models.Version.created_at.desc())
    )
    return list(db.scalars(stmt))


def count_versions(db: Session, product_id: str) -> int:
    return len(list_versions(db, product_id))
