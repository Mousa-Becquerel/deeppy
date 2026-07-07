"""
Normalize AI-extracted performance property names against the canonical names
in the family's PerformanceField registry.

The AI tends to expand canonical names with variant qualifiers:
  "Thermal transmittance (Uw) - Window 1 leaf"  →  canonical: "Thermal transmittance (Uw)"
                                                   variant:   "Window 1 leaf"
  "Watertightness (French door)"                →  canonical: "Watertightness"
                                                   variant:   "French door"
  "Sound insulation Rw - Glass"                 →  canonical: "Sound insulation (Rw)"
                                                   variant:   "Glass"

This module:
  - Picks the best matching canonical name from the family registry
  - Extracts the variant qualifier (whatever follows the canonical match)
  - Falls back to the original name + category if no canonical fits
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .enums import PerformanceCategory, ProductFamily
from .performance_registry import (
    PerformanceField,
    get_performance_fields,
    GENERIC_PERFORMANCE,
)


@dataclass
class NormalizedName:
    canonical: str               # canonical property name from ontology
    variant: Optional[str]       # variant qualifier (e.g., "French door")
    category: PerformanceCategory  # category from canonical's registry entry
    matched: bool                # True if we found a canonical match


# ─── String cleaning helpers ─────────────────────────────────────────────

_PUNCT_RE = re.compile(r"[\s\-_/]+")


def _normalize(s: str) -> str:
    """Lower-case, collapse separators, strip punctuation."""
    if not s:
        return ""
    return re.sub(r"[^\w\s()]", "", _PUNCT_RE.sub(" ", s.lower())).strip()


# ─── Canonical match search ──────────────────────────────────────────────

def _canonical_fields(family: ProductFamily) -> list[PerformanceField]:
    """Family fields + generic fallback for safety."""
    family_fields = get_performance_fields(family) or []
    # Union with GENERIC so cross-family extras (e.g., GWP) still match
    seen = {f.name for f in family_fields}
    extras = [f for f in GENERIC_PERFORMANCE if f.name not in seen]
    return family_fields + extras


def _best_match(raw_name: str, fields: list[PerformanceField]) -> Optional[PerformanceField]:
    """
    Find the canonical field whose name is the longest prefix of raw_name
    (case-insensitive, punctuation-tolerant).

    Longest match wins so that 'Glass thermal transmittance (Ug)' beats
    'Thermal transmittance' on the same input.
    """
    raw_norm = _normalize(raw_name)
    if not raw_norm:
        return None

    # Score = length of canonical's normalized form when it's a substring of raw
    best: Optional[PerformanceField] = None
    best_len = 0
    for f in fields:
        canon_norm = _normalize(f.name)
        if not canon_norm:
            continue
        if canon_norm in raw_norm and len(canon_norm) > best_len:
            best = f
            best_len = len(canon_norm)
    return best


# ─── Public API ──────────────────────────────────────────────────────────

def normalize_property_name(
    raw_name: str,
    family: ProductFamily,
    ai_category: Optional[str] = None,
) -> NormalizedName:
    """
    Normalize an AI-extracted property name to canonical + variant.

    Args:
        raw_name: The property name as Gemini returned it.
        family: Product family (drives which canonical fields to consider).
        ai_category: Category Gemini assigned; used as fallback when no
            canonical match is found.

    Returns:
        NormalizedName with canonical/variant/category/matched.
    """
    if not raw_name or not raw_name.strip():
        return NormalizedName(
            canonical=raw_name or "",
            variant=None,
            category=PerformanceCategory(ai_category) if ai_category in PerformanceCategory.__members__.values() else PerformanceCategory.OTHER,
            matched=False,
        )

    fields = _canonical_fields(family)
    match = _best_match(raw_name, fields)

    if match is None:
        # Couldn't normalize — keep original, trust AI's category
        try:
            cat = PerformanceCategory(ai_category) if ai_category else PerformanceCategory.OTHER
        except ValueError:
            cat = PerformanceCategory.OTHER
        return NormalizedName(
            canonical=raw_name.strip(),
            variant=None,
            category=cat,
            matched=False,
        )

    # Compute variant: whatever follows the canonical match in the raw_name.
    # We do a case-insensitive substring search on the ORIGINAL raw name so
    # we can slice off the suffix while keeping its case.
    variant: Optional[str] = None
    canon_lc = match.name.lower()
    raw_lc = raw_name.lower()
    pos = raw_lc.find(canon_lc)
    if pos >= 0:
        suffix = raw_name[pos + len(match.name):]
        # Strip leading separators and trailing whitespace
        suffix = suffix.strip(" \t\n-–—:()/,;")
        if suffix:
            variant = suffix
    else:
        # Canonical matched via punctuation-tolerant normalization but not as a
        # plain substring (e.g., different capitalization of parens). Fall back
        # to picking the last segment after a separator.
        sep_match = re.search(r"[\-–—:/,]\s*([^()]+)$", raw_name)
        if sep_match:
            cand = sep_match.group(1).strip()
            if cand and cand.lower() not in match.name.lower():
                variant = cand

    return NormalizedName(
        canonical=match.name,
        variant=variant or None,
        category=match.category,
        matched=True,
    )
