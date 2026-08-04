"""Post-extraction family reconciliation.

The classifier looks at each PDF one at a time and picks a `ProductFamily`
from the CPR taxonomy. It occasionally lands on a category that's plausible
from the marketing text but *wrong* given what the product is actually made
of — e.g., BIO-MORTAR (calce idraulica + biochar) landed as PTA
(pipes/tanks) instead of CEM (binders). Once composition is extracted, the
ingredients themselves are the strongest signal we have. This module
compares the classifier's consensus family against ingredient-derived
evidence and overrides when there's a strong mismatch.

Design principles:
- Only override on STRONG evidence: >= 2 ingredient hits pointing at the
  same family, AND those hits agree with each other. One-off keyword
  matches don't count.
- Leave the classifier's choice alone when the evidence is weak or absent.
  Silence is safer than a false override.
- When we do override, re-normalize performance rows against the new family
  so `is_expected` reflects the corrected ontology list — otherwise the
  frontend's "Other properties" section keeps the wrong entries.
"""
from __future__ import annotations

import logging
import re
from typing import Iterable, Optional

from ..models.passport import DigitalProductPassport
from ..ontology.enums import PerformanceCategory, ProductFamily
from ..ontology.performance_normalizer import normalize_property_name

logger = logging.getLogger(__name__)


# ─── Ingredient keyword → family ──────────────────────────────────────────
# Keys are ProductFamily values; values are keywords (lowercase, partial-match)
# that STRONGLY suggest the material belongs to that family. Keep this list
# conservative: false-positives here silently override a correct classifier
# call. Keywords appear as substrings after simple whitespace/hyphen
# normalisation (no fuzzy match).

_INGREDIENT_HINTS: dict[ProductFamily, tuple[str, ...]] = {
    # Cement / hydraulic binders — dry powder mixes activated with water.
    # Deliberately narrow so a passing mention of "cement" inside a
    # brick datasheet doesn't reclassify a MAS product as CEM.
    ProductFamily.CEM: (
        "calce idraulica", "calce naturale", "hydraulic lime", "natural lime",
        "cemento portland", "portland cement",
        "legante idraulico", "hydraulic binder",
        "malta da restauro", "restoration mortar",
        "geopolimero", "geopolymer",
        "biochar",   # bio-based binders (BIO-MORTAR class)
    ),
    # Masonry — the FINISHED unit, not the binder that lays it.
    ProductFamily.MAS: (
        "laterizio", "mattone forato", "mattone pieno", "mattone semipieno",
        "blocco in laterizio", "blocco portante", "blocco di tamponamento",
        "hollow brick", "clay brick", "clay block", "hollow clay",
        "tegola", "coppo", "roof tile",
    ),
    # Ready-mix concrete / grout / self-levelling — wet or paste form.
    ProductFamily.CMG: (
        "calcestruzzo pronto", "ready-mix concrete", "ready mix concrete",
        "boiacca", "grout", "self-leveling", "self-levelling",
        "autolivellante",
    ),
    # Insulation products — stand-alone panels/boards/rolls.
    ProductFamily.TIP: (
        "polistirene espanso", "polistirene estruso", "eps", "xps",
        "lana di roccia", "lana minerale", "rock wool", "mineral wool",
        "fibra di legno", "wood fibre",
        "poliuretano espanso", "poliuretano rigido", "pir", "pur",
        "vetro cellulare", "cellular glass",
        "aerogel",
    ),
    # Windows / doors / shutters — profiles + hardware.
    ProductFamily.DWS: (
        "profilo in alluminio", "aluminium profile", "aluminum profile",
        "profilo in pvc", "pvc profile", "u-pvc",
        "telaio in legno-alluminio", "wood-aluminium frame",
        "cerniera", "hinge", "maniglia", "handle",
        "operatore tubolare", "tubular motor",
    ),
    # Flat glass, IGUs, glass blocks — glazing components.
    ProductFamily.GLA: (
        "vetro laminato", "laminated glass", "float glass",
        "vetrocamera", "insulating glass unit", "double glazing",
        "triple glazing", "low-e", "argon", "krypton",
    ),
    # Wood-based panels — plywood, MDF, OSB, chipboard.
    ProductFamily.WBP: (
        "compensato", "plywood", "mdf", "osb", "truciolare", "chipboard",
        "particle board",
    ),
    # Gypsum products (plasterboards, etc.).
    ProductFamily.GYP: (
        "cartongesso", "plasterboard", "gypsum board",
    ),
    # Membranes — waterproofing sheets, vapour barriers.
    ProductFamily.MEM: (
        "guaina bituminosa", "bituminous membrane",
        "membrana impermeabilizzante", "waterproofing membrane",
        "epdm", "tpo",
    ),
    # Adhesives — construction glues.
    ProductFamily.ADH: (
        "colla poliuretanica", "polyurethane adhesive",
        "adesivo cementizio",   # cementitious tile adhesives
    ),
    # Sealants for joints.
    ProductFamily.SEA: (
        "silicone acetico", "silicone neutro", "acetoxy silicone",
        "neutral silicone", "sigillante poliuretanico",
        "polyurethane sealant",
    ),
}


# Minimum number of ingredient hits pointing at the same family required to
# override the classifier. 1 hit could be coincidence (e.g., a plaster
# datasheet mentioning "cement" in comparison prose). 2+ hits agreeing is
# a real signal.
_MIN_HITS_TO_OVERRIDE = 2


def _normalise(s: str) -> str:
    """Lower-case + collapse whitespace/hyphens so 'CALCE  IDRAULICA' matches
    the 'calce idraulica' keyword."""
    if not s:
        return ""
    return re.sub(r"[\s\-_]+", " ", s.lower()).strip()


def _material_descriptions(passport: DigitalProductPassport) -> list[str]:
    """Return the description text of every material in the composition."""
    out: list[str] = []
    try:
        materials = passport.composition.materials or []
    except AttributeError:
        return out
    for m in materials:
        desc = getattr(m, "description", None)
        val = getattr(desc, "value", None) if desc is not None else None
        if val:
            out.append(str(val))
    return out


def suggest_family_from_materials(passport: DigitalProductPassport) -> tuple[Optional[ProductFamily], dict]:
    """Score each family by how many of its ingredient keywords appear in
    the composition. Returns (best_family, evidence_dict) where evidence_dict
    is {family: [(keyword, matched_material_text), ...]}.

    Returns (None, {}) when no hints match anything — silent no-op path.
    """
    descs_norm = [_normalise(d) for d in _material_descriptions(passport)]
    if not descs_norm:
        return None, {}

    evidence: dict[ProductFamily, list[tuple[str, str]]] = {}
    for family, keywords in _INGREDIENT_HINTS.items():
        for kw in keywords:
            for desc in descs_norm:
                if kw in desc:
                    evidence.setdefault(family, []).append((kw, desc))

    if not evidence:
        return None, {}

    # Winner: family with the most hits. Ties → keep the classifier's choice
    # (return None so reconcile_family() falls through to the current family).
    ranked = sorted(
        ((fam, len(hits)) for fam, hits in evidence.items()),
        key=lambda x: x[1], reverse=True,
    )
    top_family, top_hits = ranked[0]
    if len(ranked) > 1 and ranked[1][1] == top_hits:
        logger.info(f"[family-reconcile] tied evidence — no override "
                    f"(top: {[(f.value, n) for f, n in ranked[:3]]})")
        return None, evidence
    return top_family, evidence


def reconcile_family(
    passport: DigitalProductPassport, current_family: ProductFamily,
) -> ProductFamily:
    """Return the family the passport SHOULD have based on composition
    ingredients. When the ingredient signal disagrees with the current
    consensus AND is strong enough, override; otherwise return current.

    Also mutates passport.metadata.product_family to match the return value
    so downstream code sees a consistent family everywhere.
    """
    suggested, evidence = suggest_family_from_materials(passport)
    if suggested is None:
        return current_family

    hit_count = len(evidence.get(suggested, []))
    if hit_count < _MIN_HITS_TO_OVERRIDE:
        logger.info(
            f"[family-reconcile] {suggested.value} suggested by {hit_count} hit(s) "
            f"— below override threshold ({_MIN_HITS_TO_OVERRIDE}); keeping {current_family.value}"
        )
        return current_family
    if suggested == current_family:
        # Classifier and ingredients agree — nothing to do.
        return current_family

    logger.info(
        f"[family-reconcile] overriding family {current_family.value} → {suggested.value} "
        f"({hit_count} ingredient hits: "
        f"{[kw for kw, _ in evidence[suggested][:5]]})"
    )

    # Update the passport's own view of the family so downstream serializers
    # and the frontend badge reflect the correction.
    #
    # Three places store the family and they MUST all agree, otherwise:
    #   • metadata.product_family              → frontend banner / stats read this
    #   • overview.product_info.product_family → frontend badge reads this
    #   • overview.product_info.product_family_code → repository.derive_hot_columns()
    #     reads THIS FIRST for the `family_code` hot column that drives list
    #     search and the AppView Model tab badge. Missing this update was why
    #     BIO-MORTAR's hot column stayed 'PTA' even after the reconciler ran
    #     (product family metadata read CEM, but every UI-visible field kept PTA).
    try:
        passport.metadata.product_family = suggested
    except AttributeError:
        pass
    _update_overview_family(passport, suggested)

    # Re-run the performance normalizer with the correct family so
    # `is_expected` reflects the corrected ontology list. Fields that were
    # previously in "Other" because they weren't in PTA's generic fallback
    # may now match CEM/MAS/etc. and move to the main section.
    _renormalize_performance(passport, suggested)

    return suggested


def _update_overview_family(passport: DigitalProductPassport, family: ProductFamily) -> None:
    """Sync overview.product_info.product_family + product_family_code with the
    reconciled family. Preserves the source/confidence attached to whichever
    field already had them, but forcibly overwrites the value + marks a note
    so a user reviewing the field can see why it changed."""
    try:
        pi = passport.overview.product_info
    except AttributeError:
        return
    note = f"Reconciled from composition ingredients (was: {getattr(getattr(pi, 'product_family_code', None), 'value', '?')!r})"
    # product_family — full descriptive name (matches enum .value)
    pf = getattr(pi, "product_family", None)
    if pf is not None:
        try:
            pf.value = family.value
            pf.confidence = "high"
            pf.note = note
        except AttributeError:
            pass
    # product_family_code — short CPR-style code (matches enum .name)
    pfc = getattr(pi, "product_family_code", None)
    if pfc is not None:
        try:
            pfc.value = family.name
            pfc.confidence = "high"
            pfc.note = note
        except AttributeError:
            pass


def _renormalize_performance(
    passport: DigitalProductPassport, family: ProductFamily,
) -> int:
    """Re-run the normalizer against the given family; update `is_expected`
    on each performance row. Returns the number of rows whose flag changed."""
    try:
        perf_values = passport.performance.values
    except AttributeError:
        return 0

    changed = 0
    for pv in perf_values:
        # normalize_property_name only reads the raw string — it doesn't need
        # the display-formatted name, which may already carry a variant suffix.
        # Strip the variant qualifier so the ontology lookup sees the canonical.
        raw = re.sub(r"\s*\([^)]*\)\s*$", "", pv.property_name).strip()
        norm = normalize_property_name(raw, family, pv.category)
        new_expected = bool(norm.matched)
        if new_expected != pv.is_expected:
            pv.is_expected = new_expected
            changed += 1
    if changed:
        logger.info(
            f"[family-reconcile] re-normalized performance rows for {family.value}: "
            f"{changed} row(s) had their is_expected flag updated"
        )
    return changed
