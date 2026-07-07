"""
SQLAlchemy ORM models for the DPP platform.

Design (hybrid): the navigable hierarchy and a few "hot" columns are
normalized; the full passport payload is stored as JSON (source of truth).

Hierarchy:  Company → Product (Model) → Batch → Item
Passport inheritance: a Batch/Item resolves its passport as the parent
Product's passport deep-merged with its own `overrides` JSON.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Company(Base):
    """A manufacturer / tenant. One seeded row for now; ready for auth later."""

    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255))
    vat: Mapped[str | None] = mapped_column(String(64), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    products: Mapped[list["Product"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
    users: Mapped[list["User"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )


class User(Base):
    """A platform user, belonging to one company. Email/password auth."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(16), default="admin")  # admin | editor | viewer
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    company: Mapped["Company"] = relationship(back_populates="users")


class Product(Base):
    """The 'Model' / General DPP. Holds the full passport as JSON."""

    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    company_id: Mapped[str | None] = mapped_column(
        ForeignKey("companies.id"), nullable=True, index=True
    )

    # Hot columns — denormalized from the passport on save for fast lists/search.
    name: Mapped[str] = mapped_column(String(512), default="Untitled Product")
    manufacturer_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    family_code: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    completeness: Mapped[float] = mapped_column(Float, default=0.0)

    # Source of truth.
    passport: Mapped[dict] = mapped_column(JSON, default=dict)
    source_documents: Mapped[list] = mapped_column(JSON, default=list)
    # Optional expert "expected results" spec for recall-vs-ground-truth scoring.
    eval_reference: Mapped[list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    company: Mapped["Company"] = relationship(back_populates="products")
    batches: Mapped[list["Batch"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    versions: Mapped[list["Version"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class Batch(Base):
    """Project DPP / production batch. Inherits the model passport + overrides."""

    __tablename__ = "batches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )

    lot: Mapped[str | None] = mapped_column(String(255), nullable=True)
    site: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    production_date: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Field-level overrides on top of the parent product's passport,
    # keyed by dotted path, e.g. {"overview.product_info.weight": "42 kg"}.
    overrides: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    product: Mapped["Product"] = relationship(back_populates="batches")
    items: Mapped[list["Item"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )


class Item(Base):
    """An individual physical unit. Inherits up the chain + own overrides."""

    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    batch_id: Mapped[str] = mapped_column(
        ForeignKey("batches.id"), nullable=False, index=True
    )

    serial_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dimensions: Mapped[str | None] = mapped_column(String(255), nullable=True)
    weight: Mapped[str | None] = mapped_column(String(64), nullable=True)
    destination: Mapped[str | None] = mapped_column(String(255), nullable=True)
    production_date: Mapped[str | None] = mapped_column(String(64), nullable=True)

    overrides: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    batch: Mapped["Batch"] = relationship(back_populates="items")


class Document(Base):
    """An uploaded source file. Bytes live on the filesystem; path stored here."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )

    filename: Mapped[str] = mapped_column(String(512))
    doc_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    family: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    product: Mapped["Product"] = relationship(back_populates="documents")


class ExtractionJob(Base):
    """A run of the extraction pipeline. Replaces the in-memory _jobs dict
    for completed jobs so results survive container restarts."""

    __tablename__ = "extraction_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    product_id: Mapped[str | None] = mapped_column(
        ForeignKey("products.id"), nullable=True, index=True
    )

    status: Mapped[str] = mapped_column(String(32), default="queued")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    stats: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Conversation(Base):
    """A chat thread about one product, for one user (persistent agent memory).

    `messages` holds the serialized pydantic-ai message history
    (ModelMessagesTypeAdapter.dump_python), reloaded per request so the agent
    itself stays stateless.
    """

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    messages: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)


class Version(Base):
    """A snapshot of a product's passport at a point in time."""

    __tablename__ = "versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )

    label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    passport_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    product: Mapped["Product"] = relationship(back_populates="versions")


class AuditLog(Base):
    """Append-only record of sensitive admin actions (H2).

    Captured for: product delete, role change, company update, user disable.
    Never modified after insert — gives us a forensic trail when something
    disappears or permissions shift.
    """

    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    company_id: Mapped[str | None] = mapped_column(
        ForeignKey("companies.id"), nullable=True, index=True
    )
    actor_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    actor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    target_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now, index=True)
