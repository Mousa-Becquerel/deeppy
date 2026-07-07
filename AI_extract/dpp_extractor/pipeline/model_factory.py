"""
Gemini model factory using pydantic-ai's direct Google AI (Generative Language API)
backend with an API key.

This avoids:
  - GCP project allowlisting for preview models (Gemini 3 etc.)
  - Service account file management
  - Vertex AI region restrictions

Get an API key at https://aistudio.google.com/apikey and set GOOGLE_API_KEY.
"""

import logging

import httpx
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from ..config import GEMINI_MODEL, GOOGLE_API_KEY

logger = logging.getLogger(__name__)

# Generous timeouts — Gemini 3 Pro with structured output + large PDFs
# can take a few minutes. httpx default read timeout is 5s, far too low.
_TIMEOUT = httpx.Timeout(
    connect=30.0,
    read=600.0,
    write=120.0,
    pool=30.0,
)


def create_gemini_model() -> GoogleModel:
    """Create a GoogleModel using the direct Gemini API with long timeouts."""
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY environment variable is not set. "
            "Get a key at https://aistudio.google.com/apikey and set it in docker-compose.yml."
        )

    provider = GoogleProvider(api_key=GOOGLE_API_KEY)

    # Override the underlying httpx client's timeout to handle long Gemini generation
    try:
        # Try a few common attribute names since pydantic-ai internals may evolve
        client = getattr(provider, "_client", None) or getattr(provider, "client", None)
        if client is not None and hasattr(client, "timeout"):
            client.timeout = _TIMEOUT
            logger.info(f"Set httpx timeout: read={_TIMEOUT.read}s, write={_TIMEOUT.write}s")
    except Exception as e:
        logger.warning(f"Could not set httpx timeout: {e}")

    logger.info(f"Initialized GoogleModel with model: {GEMINI_MODEL}")
    return GoogleModel(GEMINI_MODEL, provider=provider)
