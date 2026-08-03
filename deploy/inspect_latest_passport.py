"""Dump the most-recently created product's passport in a readable form so
we can eyeball the quality of a fresh extraction.

Usage on the EC2 (from /opt/deeppy/app):
    sudo docker cp deploy/inspect_latest_passport.py deploy-api-1:/app/inspect.py
    sudo docker exec deploy-api-1 python /app/inspect.py

Shows:
  • product metadata
  • Performance: recognized vs "Other" split (item 6 in action)
  • Manufacturer fields (grounding-guard in action)
  • Composition materials
  • Lifecycle stages summary
"""
from __future__ import annotations

import sys

from sqlalchemy import desc as sql_desc  # aliased so `desc` isn't shadowed
                                          # by a local variable in main() (a
                                          # materials-loop assignment silently
                                          # promoted `desc` to a local var and
                                          # broke the query).

from dpp_extractor.db import session_scope, models


def _val(node):
    if isinstance(node, dict) and "value" in node:
        return node["value"]
    return node


def main() -> None:
    with session_scope() as db:
        p = db.query(models.Product).order_by(sql_desc(models.Product.created_at)).first()
        if not p:
            print("no products in DB")
            return

        print("=" * 72)
        print(f"PRODUCT  {p.id[:8]}  ({p.created_at})")
        print("=" * 72)
        print(f"  name          {p.name!r}")
        print(f"  family        {p.family_code}")
        print(f"  manufacturer  {p.manufacturer_name}")
        print(f"  status        {p.status}")
        print(f"  completeness  {p.completeness}%")

        pp = p.passport or {}

        # ── Performance: expected vs other ────────────────────────────────
        vals = ((pp.get("performance") or {}).get("values")) or []
        expected = [v for v in vals if v.get("is_expected") is not False]
        other = [v for v in vals if v.get("is_expected") is False]
        print()
        print(f"PERFORMANCE  {len(vals)} rows  ({len(expected)} expected, {len(other)} other)")
        print("-" * 72)
        print("  EXPECTED:")
        for v in expected:
            cat = (v.get("category") or "?")[:11]
            name = (v.get("property_name") or "?")[:52]
            val = _val(v.get("value"))
            unit = v.get("unit") or ""
            print(f"    [{cat:11}] {name:52}  {val} {unit}".rstrip())
        if other:
            print()
            print("  OTHER (unrecognized — new 'Other properties' section):")
            for v in other:
                cat = (v.get("category") or "?")[:11]
                name = (v.get("property_name") or "?")[:52]
                val = _val(v.get("value"))
                unit = v.get("unit") or ""
                print(f"    [{cat:11}] {name:52}  {val} {unit}".rstrip())
        else:
            print("  OTHER: (none — nothing routed to unrecognized bucket)")

        # ── Manufacturer (grounding-guard's turf) ─────────────────────────
        mfr = (pp.get("overview") or {}).get("manufacturer") or {}
        print()
        print("MANUFACTURER  (post grounding-guard blanks anything not in the docs)")
        print("-" * 72)
        for k in ("company_name", "address", "website", "manufacturing_site", "email", "phone"):
            f = mfr.get(k) or {}
            v = f.get("value") if isinstance(f, dict) else None
            note = (f.get("note") if isinstance(f, dict) else None) or ""
            blanked = "grounding" in note.lower()
            marker = "  ⚠ BLANKED" if blanked else ""
            print(f"  {k:24}  {v!r:40}{marker}")
            if blanked:
                print(f"    note: {note[:150]}")

        # ── Composition ───────────────────────────────────────────────────
        mats = ((pp.get("composition") or {}).get("materials")) or []
        print()
        print(f"COMPOSITION  {len(mats)} materials")
        print("-" * 72)
        for m in mats[:12]:
            desc = _val(m.get("description")) or "?"
            pct = _val(m.get("percentage"))
            qty = _val(m.get("quantity_per_product"))
            unit = _val(m.get("unit"))
            parts = []
            if pct is not None and pct != "":
                parts.append(f"{pct}%")
            if qty is not None and qty != "":
                parts.append(f"{qty} {unit or ''}".strip())
            sup = (m.get("suppliers") or [None])[0]
            sup_name = _val(sup.get("name")) if isinstance(sup, dict) else None
            sup_str = f"  supplier: {sup_name}" if sup_name and sup_name != "-" else ""
            print(f"  {desc[:60]:60}  {' | '.join(parts) or '—':20}{sup_str}")
        if len(mats) > 12:
            print(f"  … and {len(mats) - 12} more")

        # ── Lifecycle stages ──────────────────────────────────────────────
        stages = ((pp.get("lifecycle") or {}).get("stages")) or []
        print()
        print(f"LIFECYCLE  {len(stages)} stages")
        print("-" * 72)
        for s in stages:
            code = s.get("stage_code") if isinstance(s, dict) else "?"
            gwp = _val(s.get("gwp_total") if isinstance(s, dict) else None)
            print(f"  {code:8}  GWP total: {gwp}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        raise
