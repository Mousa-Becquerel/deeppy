#!/usr/bin/env bash
# One-shot fixup: rebuild api with the current code so the SIGNUP_ALLOWLIST
# check is actually in the image, wipe the two bogus accounts my probe left,
# and confirm the gate now blocks non-listed emails.
#
# Run on the EC2 as `sudo bash deploy/fix_allowlist_deploy.sh` from the
# /opt/deeppy/app checkout.

set -euo pipefail
cd "$(dirname "$0")"

echo "=== 1. Rebuild api image (bakes in the new allowlist code) ==="
docker compose -f docker-compose.prod.yml --env-file .env up -d --build api
sleep 10

echo
echo "=== 2. Confirm SIGNUP_ALLOWLIST reached the container ==="
docker exec deploy-api-1 python -c \
  "from dpp_extractor.config import SIGNUP_ALLOWLIST; print(sorted(SIGNUP_ALLOWLIST))"

echo
echo "=== 3. Delete bogus accounts (stranger@example.com, test1@levery.it) ==="
docker exec deploy-api-1 python - <<'PYEOF'
from dpp_extractor.db import session_scope, models

with session_scope() as db:
    for email in ("stranger@example.com", "test1@levery.it"):
        u = db.query(models.User).filter(models.User.email == email).first()
        if not u:
            print(f"  {email}: not found (skipping)")
            continue
        cid = u.company_id
        db.delete(u)
        db.flush()
        c = db.get(models.Company, cid) if cid else None
        if c and not c.users:
            db.delete(c)
            print(f"  {email}: deleted (+ orphan company {cid[:8]})")
        else:
            print(f"  {email}: deleted (company kept, still has other users)")
PYEOF

echo
echo "=== 4. Verify from outside: unlisted email should now 403 ==="
curl -s -o - -w '\nHTTP %{http_code}\n' \
  -X POST https://deeppy.eu/api/auth/register \
  -H 'Content-Type: application/json' \
  --data-raw '{"company_name":"Nope","email":"stranger2@example.com","password":"anything12345","name":"X"}'

echo
echo "=== 5. Verify listed email would be accepted (dry-run — status check only) ==="
docker exec deploy-api-1 python -c \
  "from dpp_extractor.config import SIGNUP_ALLOWLIST; e='test2@levery.it'; print(f'{e} on allowlist: {e in SIGNUP_ALLOWLIST}')"

echo
echo "Done. If Step 4 returned HTTP 403 with 'invite-only' — the gate is live."
