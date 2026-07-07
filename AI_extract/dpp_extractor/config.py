"""
Configuration for the DPP extraction pipeline.

Loads settings from environment variables or .env file.
Mirrors the GCP setup used in energy_bill_extractor.py.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from AI_extract directory
_AI_EXTRACT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_AI_EXTRACT_DIR / ".env")


# ---------------------------------------------------------------------------
# Google Generative Language API (AI Studio)
# Direct access — no Vertex AI / GCP project / allowlisting required.
# Get an API key at https://aistudio.google.com/apikey
# ---------------------------------------------------------------------------
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

# ---------------------------------------------------------------------------
# Assistant (OpenAI) — separate from extraction. Chat agent uses OpenAI; the
# extraction pipeline keeps using Gemini. Set OPENAI_API_KEY to enable chat.
# ---------------------------------------------------------------------------
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1")

# Legacy Vertex AI settings — kept for documentation, no longer used by model_factory
GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "alpinvision")
GCP_REGION: str = os.getenv("GCP_REGION", "europe-west4")
GCP_SERVICE_ACCOUNT_FILE: str = os.getenv(
    "GCP_SERVICE_ACCOUNT_FILE",
    str(_AI_EXTRACT_DIR / "service_account.json"),
)

# ---------------------------------------------------------------------------
# Pipeline tuning
# ---------------------------------------------------------------------------
MAX_CONCURRENT_EXTRACTIONS: int = int(os.getenv("MAX_CONCURRENT", "2"))
MAX_PDF_SIZE_MB: int = int(os.getenv("MAX_PDF_SIZE_MB", "50"))
SUPPORTED_MIME_TYPES: list[str] = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/tiff",
]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SAMPLE_DOCS_DIR: Path = _AI_EXTRACT_DIR.parent / "DPP_products"
OUTPUT_DIR: Path = _AI_EXTRACT_DIR / "output"

# ---------------------------------------------------------------------------
# Persistence
# Default to a SQLite file under DATA_DIR. In Docker this is a mounted volume
# (/app/data) so the database survives container rebuilds. Set DATABASE_URL to
# a postgresql:// URL to migrate to Postgres later — no code changes needed.
# ---------------------------------------------------------------------------
DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(_AI_EXTRACT_DIR / "data")))
UPLOADS_DIR: Path = Path(os.getenv("UPLOADS_DIR", str(_AI_EXTRACT_DIR / "uploads")))
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{(DATA_DIR / 'deeppy.db').as_posix()}",
)

# ---------------------------------------------------------------------------
# Authentication
# JWT_SECRET MUST be set to a strong random value in production (env var).
# The dev default is fine for local use but is NOT secure for deployment.
# ---------------------------------------------------------------------------
# ENVIRONMENT gates production-hardened defaults below.
# Values: "development" (default), "staging", "production"
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION: bool = ENVIRONMENT in ("production", "prod")

# The development default is intentionally insecure. In production, set
# JWT_SECRET to a strong random value (e.g. `openssl rand -hex 32`). The
# startup hook refuses to boot if this default is used with ENVIRONMENT=production.
JWT_SECRET_DEV_DEFAULT = "dev-insecure-change-me-in-production"
# `or` (not the os.getenv default) so an empty-string env var — e.g. when
# docker-compose expands `${JWT_SECRET:-}` against a host without the var set —
# falls back to the dev default instead of signing JWTs with an empty HMAC key
# (which raises InvalidKeyError on every login).
JWT_SECRET: str = os.getenv("JWT_SECRET") or JWT_SECRET_DEV_DEFAULT
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "12"))
AUTH_COOKIE_NAME: str = "deeppy_session"
# COOKIE_SECURE defaults to true in production (HTTPS required), false otherwise.
# Explicit env var overrides the default either way.
_cookie_secure_env = os.getenv("COOKIE_SECURE")
COOKIE_SECURE: bool = (
    _cookie_secure_env.lower() == "true"
    if _cookie_secure_env is not None
    else IS_PRODUCTION
)
