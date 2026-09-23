"""Turn public DPP access on/off for specific products.

Sept 23 client feedback: only "Lightweight concrete agrobuilder" and
"Biomortar agrobuilder" should open as a full public DPP from the landing
page. Every other published product still shows as a card, but its passport
is gated behind a session.

Run inside the api container:

    # show current state, change nothing
    sudo docker exec deploy-api-1 python /opt/app/deploy/set_public_access.py --list

    # grant to the two the client named (default set)
    sudo docker exec deploy-api-1 python /opt/app/deploy/set_public_access.py --apply

    # arbitrary product, by name fragment / display id / uuid
    sudo docker exec deploy-api-1 python /opt/app/deploy/set_public_access.py --apply --grant "biochar"
    sudo docker exec deploy-api-1 python /opt/app/deploy/set_public_access.py --apply --revoke DPP-M-0009

Without --apply it is a dry run. Matching is case-insensitive on a substring
of the product name, and also accepts a uuid or a DPP-M-#### display id.
Anything that matches nothing is reported loudly rather than skipped silently,
because a typo here means the client sees a locked card and assumes we
ignored them.
"""
from __future__ import annotations

import argparse
import re
import sys

# The two the client asked for, as name fragments so small renames
# ("...01", " AGROBUILDER") still match.
DEFAULT_GRANT = ["lightweight concrete", "biomortar"]

_DISPLAY_RE = re.compile(r"^DPP-M-0*(\d+)$", re.IGNORECASE)


def _resolve(db, models, token: str) -> list:
    """Products matching a uuid, a DPP-M-#### display id, or a name fragment."""
    m = _DISPLAY_RE.match(token.strip())
    if m:
        p = (db.query(models.Product)
               .filter(models.Product.public_id == int(m.group(1))).first())
        return [p] if p else []

    p = db.get(models.Product, token.strip())
    if p:
        return [p]

    like = f"%{token.strip()}%"
    return (db.query(models.Product)
              .filter(models.Product.name.ilike(like))
              .order_by(models.Product.public_id).all())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--list", action="store_true", help="show every published product and exit")
    ap.add_argument("--grant", action="append", default=[], metavar="TOKEN")
    ap.add_argument("--revoke", action="append", default=[], metavar="TOKEN")
    args = ap.parse_args()

    from dpp_extractor.db import session_scope
    from dpp_extractor.db import models

    with session_scope() as db:
        if args.list:
            rows = (db.query(models.Product)
                      .order_by(models.Product.public_id).all())
            print(f"{'id':>5}  {'public':<7} {'status':<10} name")
            for p in rows:
                did = f"M-{p.public_id:04d}" if p.public_id is not None else "—"
                print(f"{did:>7}  {str(bool(p.public_access)):<7} {p.status:<10} {p.name}")
            return 0

        grant = args.grant or DEFAULT_GRANT
        revoke = args.revoke

        changed, missing = [], []
        for token, value in [(t, True) for t in grant] + [(t, False) for t in revoke]:
            hits = _resolve(db, models, token)
            if not hits:
                missing.append(token)
                continue
            for p in hits:
                if bool(p.public_access) == value:
                    print(f"  = already {value}: {p.name}")
                    continue
                print(f"  {'+' if value else '-'} {p.name}  (status={p.status})")
                if p.status != "published" and value:
                    print(f"      NOTE: not published — it will stay hidden until it is")
                changed.append((p, value))

        for p, value in changed:
            if args.apply:
                p.public_access = value
        if args.apply:
            db.flush()

        print()
        if missing:
            print(f"NO MATCH for: {missing}  <-- check the name, nothing was set for these")
        print(f"{len(changed)} product(s) {'updated' if args.apply else 'would change (dry run)'}")
        if not args.apply:
            print("re-run with --apply to write")
        return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
