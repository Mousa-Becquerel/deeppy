"""H3 — every response carries the security-header set."""


def _assert_headers(headers):
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "Permissions-Policy" in headers
    csp = headers.get("Content-Security-Policy", "")
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp


def test_headers_on_health_endpoint(client):
    _assert_headers(client.get("/api/health").headers)


def test_headers_on_401_response(client):
    # 401 still must carry the headers — middleware runs on errors too.
    _assert_headers(client.get("/api/auth/me").headers)


def test_no_hsts_in_dev_mode(client):
    """HSTS would force HTTPS on localhost. Only emit it in production."""
    assert "Strict-Transport-Security" not in client.get("/api/health").headers
