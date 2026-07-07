"""
Database engine, session, and base class.

Dialect-agnostic: SQLite today, Postgres later. The only SQLite-specific bit
is the check_same_thread connect arg, applied conditionally.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ..config import DATABASE_URL, IS_PRODUCTION

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


_IS_SQLITE = DATABASE_URL.startswith("sqlite")

# SQLite + FastAPI's threadpool requires check_same_thread=False.
# Postgres ignores it.
_connect_args = {"check_same_thread": False} if _IS_SQLITE else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    future=True,
    pool_pre_ping=True,
)


# B4: enable SQLite WAL mode + sensible pragmas for concurrent reads while
# writes serialize. Reduces "database is locked" errors in dev/single-instance
# deployments. Postgres ignores this; production should use Postgres anyway.
if _IS_SQLITE:
    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(dbapi_conn, _connection_record):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA synchronous=NORMAL")
        cur.execute("PRAGMA busy_timeout=5000")        # ms — wait up to 5s for a lock
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    if IS_PRODUCTION:
        logger.warning(
            "Running on SQLite in PRODUCTION mode — SQLite is not suitable "
            "for multi-worker deployments. Switch DATABASE_URL to a "
            "postgresql://... URL before scaling beyond a single process."
        )

SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, future=True
)


def init_db() -> None:
    """Bring the schema up to date.

    Strategy:
      1. Try Alembic `upgrade head` (the production-correct path — applies any
         pending migrations and idempotently no-ops if already at head).
      2. Fall back to `Base.metadata.create_all` if Alembic isn't configured
         (e.g. running from a packaged build without the alembic/ tree).
    """
    from . import models  # noqa: F401 — register models on Base.metadata

    try:
        from pathlib import Path
        from alembic import command
        from alembic.config import Config

        # alembic.ini lives next to AI_extract/ in the container (/app/alembic.ini)
        candidate_paths = [
            Path("/app/alembic.ini"),
            Path(__file__).resolve().parents[3] / "alembic.ini",
        ]
        cfg_path = next((p for p in candidate_paths if p.exists()), None)
        if cfg_path:
            cfg = Config(str(cfg_path))
            cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
            command.upgrade(cfg, "head")
            logger.info(f"Database migrated to head: {DATABASE_URL}")
            return
    except Exception:
        logger.exception("Alembic upgrade failed; falling back to create_all")

    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialized (create_all fallback): {DATABASE_URL}")


def get_session() -> Iterator[Session]:
    """FastAPI dependency — yields a session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Context manager for use outside request handlers (background tasks).

    Commits on success, rolls back on exception, always closes.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
