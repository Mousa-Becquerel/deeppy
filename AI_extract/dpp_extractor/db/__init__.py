"""
Persistence layer for the DPP platform.

SQLite for now (file under DATA_DIR), Postgres-ready via SQLAlchemy.
Switch by setting DATABASE_URL to a postgresql:// URL — no code changes.
"""

from .database import Base, engine, SessionLocal, get_session, init_db, session_scope

__all__ = ["Base", "engine", "SessionLocal", "get_session", "init_db", "session_scope"]
