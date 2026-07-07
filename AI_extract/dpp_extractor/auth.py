"""
Authentication core — bcrypt password hashing + JWT session tokens.

The token is carried in an httpOnly, SameSite=Lax cookie (set/cleared by the
API). `get_current_user` is a FastAPI dependency that validates the cookie and
returns a lightweight, detached user dict (no open DB session held).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Cookie, Depends, HTTPException, status

from .config import (
    AUTH_COOKIE_NAME,
    JWT_ALGORITHM,
    JWT_EXPIRE_HOURS,
    JWT_SECRET,
)
from .db import session_scope
from .db import models


# ── Passwords ──────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ── JWT ────────────────────────────────────────────────────────────────────

def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


# ── Current-user dependency ──────────────────────────────────────────────────

def _user_to_dict(u: "models.User") -> dict:
    return {
        "id": u.id,
        "company_id": u.company_id,
        "email": u.email,
        "name": u.name,
        "role": u.role,
        "is_active": u.is_active,
    }


async def get_current_user(
    session_cookie: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME),
) -> dict:
    """Validate the session cookie → return the current user dict, or 401."""
    if not session_cookie:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    payload = decode_access_token(session_cookie)
    if not payload or "sub" not in payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired session")
    with session_scope() as db:
        user = db.get(models.User, payload["sub"])
        if not user or not user.is_active:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")
        return _user_to_dict(user)


def require_role(*allowed: str):
    """Dependency factory — 403 unless the current user has one of the roles."""
    async def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return checker
