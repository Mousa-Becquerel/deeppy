"""
In-process token-bucket rate limiter for auth endpoints (H1).

Single-process only — fine for the current single-container deployment. When we
scale beyond one process we switch this to Redis (uvicorn + Postgres run on
one host today; the limiter would otherwise diverge per worker).

Default: 5 requests per 60 seconds per (client_ip, key).  Keyed by IP only
when a per-account key isn't available, or by IP+lowercased-email when it is.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass

from fastapi import HTTPException, Request


@dataclass
class _Bucket:
    tokens: float
    last: float


class TokenBucketLimiter:
    """Classic token bucket. Thread-safe via a single lock — at our QPS the
    contention is negligible and the simplicity is worth it."""

    def __init__(self, capacity: int = 5, refill_per_sec: float = 5 / 60):
        self.capacity = float(capacity)
        self.refill_per_sec = refill_per_sec
        self._buckets: dict[str, _Bucket] = {}
        self._lock = threading.Lock()

    def _take(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            b = self._buckets.get(key)
            if b is None:
                b = _Bucket(tokens=self.capacity, last=now)
                self._buckets[key] = b
            # Refill since last hit.
            elapsed = now - b.last
            b.tokens = min(self.capacity, b.tokens + elapsed * self.refill_per_sec)
            b.last = now
            if b.tokens < 1.0:
                return False
            b.tokens -= 1.0
            return True

    def check(self, key: str, retry_after: int = 60) -> None:
        """Take one token or raise 429.

        retry_after is exposed in the response header so well-behaved clients
        back off."""
        if not self._take(key):
            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Try again in a minute.",
                headers={"Retry-After": str(retry_after)},
            )

    def reset(self, key: str | None = None) -> None:
        """Test helper — wipe one bucket or all of them."""
        with self._lock:
            if key is None:
                self._buckets.clear()
            else:
                self._buckets.pop(key, None)


# Singleton used by the login endpoint. Capacity 5 / window 60s → 5 attempts
# per minute per (IP, email).  Refill is 5/60 ≈ 0.083 tok/s.
login_limiter = TokenBucketLimiter(capacity=5, refill_per_sec=5 / 60)


def client_ip(request: Request) -> str:
    """Best-effort client IP for rate-limit keys. Honours X-Forwarded-For so
    deployments behind a reverse proxy don't bucket every client under the
    proxy's address; falls back to the socket peer if the header is absent."""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        # First entry is the original client when set by a trusted proxy.
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
