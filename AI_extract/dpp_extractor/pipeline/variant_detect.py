"""Detect product-variant qualifiers in extracted performance rows.

The client's canonical case: a brick DoP that declares 5 thicknesses. The
AI faithfully extracts one performance row per thickness, so `passport.
performance.values` contains something like:

    Thermal transmittance (Uw) (window, 1 leaf)   0.63 W/m²K
    Thermal transmittance (Uw) (window, 2 leaves) 0.69 W/m²K
    Thermal transmittance (Uw) (door, 1 leaf)     0.65 W/m²K
    Sound insulation (Rw) (glass)                 42 dB

This module scans property_name strings, extracts parenthesized qualifiers
(the "(window, 1 leaf)" bits), and returns the set of qualifiers that
appear on multiple canonical properties. The UI uses that set to offer a
"which SKU is this passport for?" selector.

Kept in a separate module so it can be tested without spinning up the whole
pipeline.
"""
from __future__ import annotations

import logging
import re
from collections import Counter, defaultdict
from typing import Iterable

from ..models.passport import DigitalProductPassport

logger = logging.getLogger(__name__)

_QUALIFIER_RE = re.compile(r"\(([^)]+)\)\s*$")

# Anything wrapped in square brackets is a unit tag added by the extractor
# (e.g. "Recycled content ([%])" → qualifier == "[%]"), never a real SKU
# variant. Same for percentage-only strings.
_BRACKETED_UNIT_RE = re.compile(r"^\[[^\]]+\]$")

# Qualifiers that are NEVER product-variant tags — they're units, method
# labels, or measurement contexts. Filter them out so we don't offer the user
# a "which SKU?" prompt for "(class)" or "(Uw)".
_NON_VARIANT_QUALIFIERS = {
    "class", "classe", "value", "valore", "min", "max",
    "average", "media", "peak", "typical", "tipico",
    "measured", "misurato", "declared", "dichiarato",
    # canonical unit-like labels the normalizer sometimes leaves as qualifiers
    "uw", "ug", "uf", "psi", "lambda", "rw", "u", "r",
    # common unit shorthands the extractor sometimes appends as a qualifier
    "%", "kgco2eq", "m3", "m2", "mj", "kg", "kwh", "n/mm2", "n/mm²",
    "w/mk", "w/m²k", "w/mk²", "mm", "cm", "m",
}


def _strip_qualifier(name: str) -> tuple[str, str | None]:
    """Return (base_name_without_trailing_paren, qualifier_or_None)."""
    m = _QUALIFIER_RE.search(name or "")
    if not m:
        return name, None
    base = name[: m.start()].strip()
    qual = m.group(1).strip()
    if qual.lower() in _NON_VARIANT_QUALIFIERS:
        return name, None   # keep the qualifier — it's a unit/method, not a variant
    if _BRACKETED_UNIT_RE.match(qual):
        return name, None   # "[%]" / "[kgCO2eq]" — extractor-added unit tag, not a variant
    return base, qual


def detect_variants(passport: DigitalProductPassport) -> list[str]:
    """Return the set of qualifier strings that behave like SKU variants —
    i.e. that appear on more than one canonical property (proving they're
    describing a variant, not a one-off measurement condition).

    Ordered by frequency (most common first), which is how the UI displays
    them and how a sensible auto-select would pick the "primary" variant.
    """
    try:
        perf_values = passport.performance.values or []
    except AttributeError:
        return []

    # Map qualifier → set of canonical base names it appears on.
    qualifier_bases: dict[str, set[str]] = defaultdict(set)
    for pv in perf_values:
        base, qual = _strip_qualifier(pv.property_name or "")
        if qual:
            qualifier_bases[qual].add(base.lower())

    # A real variant appears on ≥2 different base properties. A qualifier
    # that shows up under just one property is probably a one-off comment
    # (e.g., "(low-e coating side)" on a single glass row).
    variants = [
        (q, len(bases)) for q, bases in qualifier_bases.items()
        if len(bases) >= 2
    ]
    if not variants:
        return []

    # Order by (base-count, then total occurrences) so the primary variant —
    # the one describing the most properties — is first.
    occurrence = Counter()
    for pv in perf_values:
        _, qual = _strip_qualifier(pv.property_name or "")
        if qual:
            occurrence[qual] += 1

    variants.sort(key=lambda x: (-x[1], -occurrence[x[0]], x[0]))
    ordered = [q for q, _ in variants]
    logger.info(f"[variant-detect] found {len(ordered)} variants: {ordered}")
    return ordered


def populate_detected_variants(passport: DigitalProductPassport) -> None:
    """Post-processing hook — writes detected_variants into passport.metadata.
    No-op when only one (or zero) variants surface."""
    try:
        variants = detect_variants(passport)
        passport.metadata.detected_variants = variants
    except AttributeError:
        logger.warning("[variant-detect] passport.metadata unavailable; skipping")
