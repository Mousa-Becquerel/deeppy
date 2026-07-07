"""
Append-only audit log helper (H2).

Use record() inside a session_scope() block to capture an admin action.
Failures here are swallowed and logged — we never want a logging hiccup to
break a successful user action.
"""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from .db import models

logger = logging.getLogger(__name__)


def record(
    db: Session,
    *,
    action: str,
    actor: Optional[dict] = None,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    detail: Optional[dict] = None,
    ip: Optional[str] = None,
) -> None:
    """Append one entry. `actor` is the current_user dict from auth.

    Action vocabulary (extend as needed):
      product.delete, product.role_change, company.update,
      user.disable, user.role_change
    """
    try:
        entry = models.AuditLog(
            company_id=(actor or {}).get("company_id"),
            actor_user_id=(actor or {}).get("id"),
            actor_email=(actor or {}).get("email"),
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
            ip=ip,
        )
        db.add(entry)
        db.flush()
    except Exception:
        logger.exception(f"Failed to record audit entry: action={action}")


def list_for_company(
    db: Session, company_id: str, limit: int = 200
) -> list[models.AuditLog]:
    """Read recent entries for a company. Admin-only via endpoint."""
    from sqlalchemy import select
    stmt = (
        select(models.AuditLog)
        .where(models.AuditLog.company_id == company_id)
        .order_by(models.AuditLog.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))
