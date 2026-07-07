"""
Pass 3 — Cross-document merge and reconciliation.

Merges extraction outputs from multiple documents into a single
DigitalProductPassport, resolving conflicts using document authority rules.

Authority hierarchy (higher wins):
  - Performance data:  DoP > TechnicalSheet > EPD > Certificate
  - Environmental data: EPD > DoP > TechnicalSheet
  - Safety data:        SDS > DoP > Certificate
  - Manufacturer info:  DoP > TechnicalSheet > Catalog > EPD
  - Composition/BoM:    BOM > TechnicalSheet > EPD
"""

import logging
from typing import Optional

from ..models.common import ExtractedField, SourceReference
from ..models.classification import DocumentClassification
from ..models.extraction_output import DocumentExtractionOutput
from ..models.passport import DigitalProductPassport, PassportMetadata
from ..models.merge_result import MergeResult, MergeConflict
from ..ontology.enums import DocumentType, ProductFamily, ConfidenceLevel
from ..ontology.field_priority import get_field_priority

logger = logging.getLogger(__name__)

# Document authority rankings per data domain (lower index = higher authority).
# Source: DeePPy_data_ontology.xlsx → Data_ontology priority columns.
# For Performance fields the ontology says: DoP=1, CE=2, EPD=3, TechSheet=4.
PERFORMANCE_AUTHORITY = [
    DocumentType.DOP, DocumentType.CERTIFICATE,
    DocumentType.EPD, DocumentType.TECHNICAL_SHEET,
]
ENVIRONMENTAL_AUTHORITY = [
    DocumentType.EPD, DocumentType.DOP, DocumentType.TECHNICAL_SHEET,
]
SAFETY_AUTHORITY = [
    DocumentType.SDS, DocumentType.DOP, DocumentType.CERTIFICATE,
]
MANUFACTURER_AUTHORITY = [
    DocumentType.DOP, DocumentType.TECHNICAL_SHEET,
    DocumentType.CATALOG, DocumentType.EPD,
]
COMPOSITION_AUTHORITY = [
    DocumentType.BOM, DocumentType.TECHNICAL_SHEET, DocumentType.EPD,
]


def _authority_rank(doc_type: DocumentType, authority_list: list[DocumentType]) -> int:
    """Get the authority rank for a document type. Lower = higher authority."""
    try:
        return authority_list.index(doc_type)
    except ValueError:
        return len(authority_list)  # Unknown types get lowest priority


# Sections where a sub-component document's data is meaningless or misleading.
# A glass DoP attached to a window upload should NEVER win:
#   - overview fields (product_name, manufacturer, address, etc.)
#   - compliance scalar fields (dop_reference, ce_marking, safety questions)
# Sub-component data IS valuable for composition (BoM enrichment),
# performance values (the glass contributes to the Uw of the assembly),
# and product_certifications/company_certifications lists (additive).
_SUBCOMPONENT_BLOCKED_SECTIONS = (
    "overview",
    "compliance.dop_reference",
    "compliance.dop_standard",
    "compliance.doc_reference",
    "compliance.ce_marking",
    "compliance.quality_control",
    "compliance.safety",
    "compliance.other_labels",
)


def _filter_subcomponent_candidates(
    candidates: list[tuple[ExtractedField, DocumentType, str]],
    field_path: str,
    consensus_family: Optional[ProductFamily],
) -> list[tuple[ExtractedField, DocumentType, str]]:
    """
    For overview fields, drop candidates that came from sub-component documents
    (i.e., documents whose source_family disagrees with the consensus).

    For composition/lifecycle/performance, keep all candidates — sub-component
    data is valuable there (a glass DoP enriches the BoM).

    If filtering would leave no candidates, returns the original list (better to
    have wrong-source data than no data, and the user can correct it).
    """
    if consensus_family is None:
        return candidates
    if not field_path.startswith(_SUBCOMPONENT_BLOCKED_SECTIONS):
        return candidates

    def _is_main_doc(field: ExtractedField) -> bool:
        # Trust the candidate if we can't determine its family
        if field.source is None or field.source.source_family is None:
            return True
        return field.source.source_family == consensus_family

    main = [c for c in candidates if _is_main_doc(c[0])]
    if main:
        return main
    return candidates  # Fall back to all when nothing matches consensus


def _pick_best_field(
    candidates: list[tuple[ExtractedField, DocumentType, str]],
    authority: list[DocumentType],
    field_path: str,
    conflicts: list[MergeConflict],
    consensus_family: Optional[ProductFamily] = None,
) -> ExtractedField:
    """
    Pick the best value from multiple candidates.

    Args:
        candidates: List of (field, doc_type, doc_name) tuples.
        authority: Section-level authority ranking (fallback when no per-field priority).
        field_path: Dot-path for conflict tracking and per-field priority lookup.
        conflicts: List to append conflicts to.
        consensus_family: Product family agreed across all docs. Used to filter
            sub-component documents out of overview-section merges.

    Returns:
        The winning ExtractedField.
    """
    # Drop sub-component documents from overview fields BEFORE applying authority.
    # A glass DoP can't be the "manufacturer" of a window — even if it's a DoP.
    candidates = _filter_subcomponent_candidates(candidates, field_path, consensus_family)

    # Per-field priority overrides section authority when defined
    # (from DeePPy_data_ontology.xlsx → Data_ontology priority columns)
    field_specific_priority = get_field_priority(field_path)
    effective_authority = field_specific_priority if field_specific_priority else authority

    # Filter to only filled candidates
    filled = [(f, dt, dn) for f, dt, dn in candidates if f.is_filled]
    if not filled:
        # Return the first candidate (empty) if none are filled
        return candidates[0][0] if candidates else ExtractedField()

    if len(filled) == 1:
        return filled[0][0]

    # Multiple values — check if they agree
    values = set()
    for f, _, _ in filled:
        val = str(f.value).strip().lower() if f.value else ""
        values.add(val)

    if len(values) == 1:
        # All agree — pick the one with highest confidence, then highest authority
        filled.sort(key=lambda x: (
            -[ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW].index(x[0].confidence),
            _authority_rank(x[1], effective_authority),
        ))
        return filled[0][0]

    # Conflict — record it and pick by authority then confidence
    conflict = MergeConflict(
        field_path=field_path,
        values=[
            {"document": dn, "value": str(f.value), "confidence": f.confidence.value}
            for f, _, dn in filled
        ],
    )

    filled.sort(key=lambda x: (
        _authority_rank(x[1], effective_authority),
        -[ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW].index(x[0].confidence),
    ))

    winner_field, winner_type, winner_name = filled[0]
    conflict.resolved_value = str(winner_field.value)
    conflict.resolved_source = winner_type
    if field_specific_priority:
        conflict.resolution_reason = (
            f"{winner_type.value} is the preferred source for {field_path} (per ontology)"
        )
    else:
        conflict.resolution_reason = (
            f"{winner_type.value} has higher authority for {field_path.split('.')[0]} data"
        )
    conflicts.append(conflict)

    # Downgrade confidence to MEDIUM since there was a conflict
    if winner_field.confidence == ConfidenceLevel.HIGH:
        winner_field = winner_field.model_copy(update={"confidence": ConfidenceLevel.MEDIUM})
        if not winner_field.note:
            winner_field = winner_field.model_copy(
                update={"note": f"Conflict resolved: chose {winner_name} over other sources"}
            )

    return winner_field


def _get_authority_for_section(section_name: str) -> list[DocumentType]:
    """Map section name to the appropriate authority list."""
    mapping = {
        "overview": MANUFACTURER_AUTHORITY,
        "composition": COMPOSITION_AUTHORITY,
        "performance": PERFORMANCE_AUTHORITY,
        "compliance": SAFETY_AUTHORITY,
        "lifecycle": ENVIRONMENTAL_AUTHORITY,
    }
    return mapping.get(section_name, MANUFACTURER_AUTHORITY)


def merge_extractions(
    extractions: list[tuple[DocumentExtractionOutput, DocumentClassification, str]],
    product_family: ProductFamily,
) -> tuple[DigitalProductPassport, MergeResult]:
    """
    Merge multiple per-document extractions into a single passport.

    Args:
        extractions: List of (extraction_output, classification, filename) tuples.
        product_family: The detected product family (from Pass 1 consensus).

    Returns:
        (DigitalProductPassport, MergeResult) tuple.
    """
    conflicts: list[MergeConflict] = []

    passport = DigitalProductPassport(
        metadata=PassportMetadata(
            product_family=product_family,
            source_documents=[fn for _, _, fn in extractions],
        )
    )

    # Merge each section by iterating fields
    for section_name in ["overview", "composition", "compliance"]:
        target_section = getattr(passport, section_name)
        authority = _get_authority_for_section(section_name)

        _merge_section_fields(
            target_section, section_name, extractions, authority, conflicts,
            consensus_family=product_family,
        )

    # Performance: merge the values lists
    _merge_performance(passport, extractions, conflicts)

    # Lifecycle: merge A3 manufacturing + EPD stages
    _merge_lifecycle(passport, extractions, conflicts)

    # Lists that aren't covered by the field-by-field merger:
    # composition.materials, compliance.product_certifications, compliance.company_certifications.
    # Strategy: union across all docs, deduplicating by description / cert name.
    _merge_composition_materials(passport, extractions)
    _merge_certifications(passport, extractions)

    # Build merge result stats
    merge_result = _build_merge_stats(passport, extractions, conflicts)

    logger.info(
        f"Merge complete: {merge_result.total_fields_filled}/{merge_result.total_fields} fields, "
        f"{len(conflicts)} conflicts"
    )

    return passport, merge_result


def _merge_section_fields(
    target_section,
    section_name: str,
    extractions: list[tuple[DocumentExtractionOutput, DocumentClassification, str]],
    authority: list[DocumentType],
    conflicts: list[MergeConflict],
    consensus_family: Optional[ProductFamily] = None,
) -> None:
    """Merge ExtractedField attributes of a section across documents."""
    for field_name in target_section.model_fields:
        target_val = getattr(target_section, field_name)

        # Only merge ExtractedField instances (skip nested models and lists)
        if not isinstance(target_val, ExtractedField):
            # Handle nested BaseModel (e.g., overview.product_info, overview.manufacturer)
            nested = target_val
            if hasattr(nested, "model_fields"):
                _merge_section_fields(
                    nested, f"{section_name}.{field_name}",
                    extractions, authority, conflicts,
                    consensus_family=consensus_family,
                )
            continue

        # Collect candidates from all documents
        candidates = []
        for extraction, classification, filename in extractions:
            source_section = _resolve_dot_path(extraction, section_name)
            if source_section is None:
                continue
            source_val = _get_nested_field(source_section, field_name)
            if source_val is not None and isinstance(source_val, ExtractedField):
                candidates.append((source_val, classification.document_type, filename))

        if candidates:
            best = _pick_best_field(
                candidates, authority, f"{section_name}.{field_name}", conflicts,
                consensus_family=consensus_family,
            )
            setattr(target_section, field_name, best)


def _resolve_dot_path(obj, dot_path: str):
    """Resolve a dot-separated path like 'overview.product_info' on an object."""
    current = obj
    for part in dot_path.split("."):
        current = getattr(current, part, None)
        if current is None:
            return None
    return current


def _get_nested_field(section, field_name: str):
    """Try to get a field from a section, handling nested models."""
    if hasattr(section, field_name):
        return getattr(section, field_name)
    # Try nested — e.g., for overview, check product_info and manufacturer
    for attr_name in section.model_fields:
        nested = getattr(section, attr_name)
        if hasattr(nested, field_name):
            return getattr(nested, field_name)
    return None


import re as _re

# Catalog noise patterns: parenthetical qualifiers that mark cross-product
# or per-plant tables in commercial catalogs. When the authoritative DoP /
# Certificate / Technical Sheet / EPD has already given a clean canonical
# value, drop these noisy alternates.
# Match a plant/site name appearing anywhere inside a parenthetical qualifier,
# e.g. "(Bubano)", "(Terni - muratura)", "([kg/m3] (Terni - solaio)".
_PLANT_QUALIFIER_RE = _re.compile(
    r"\b(?:bubano|feltre|terni|gattinara|mordano)\b",
    _re.IGNORECASE,
)
_CROSS_PRODUCT_RE = _re.compile(
    r"(?:plan\s*\d+|thermal\s*t\s*\d+|bio\s*mod\s*sonico|terracoat|"
    r"wall\s*force(?:\s*compact)?|wienerberger\s*e-tabs)",
    _re.IGNORECASE,
)


def _is_catalog_noise(property_name: str) -> bool:
    """Detect catalog-noise performance entries (per-plant tables, cross-product variants)."""
    if not property_name:
        return False
    return bool(
        _PLANT_QUALIFIER_RE.search(property_name)
        or _CROSS_PRODUCT_RE.search(property_name)
    )


def _strip_qualifier(property_name: str) -> str:
    """Strip parenthetical qualifiers from a property name to get its canonical key."""
    return _re.sub(r"\s*\([^)]*\)\s*", "", property_name).strip().lower()


_AUTHORITATIVE_FOR_PERF = {
    DocumentType.DOP,
    DocumentType.CERTIFICATE,
    DocumentType.TECHNICAL_SHEET,
    DocumentType.EPD,
}


def _merge_performance(passport, extractions, conflicts) -> None:
    """Merge performance values from all documents.

    Filters out catalog noise: per-plant table entries and cross-product
    variants whose canonical property already has an authoritative value.
    """
    all_values = {}  # name → list of (PerformanceValue, doc_type, filename)

    # Track which canonical property names have authoritative coverage
    authoritative_canonicals: set[str] = set()
    for extraction, classification, filename in extractions:
        if classification.document_type in _AUTHORITATIVE_FOR_PERF:
            for pv in extraction.performance.values:
                if pv.value and pv.value.value:
                    authoritative_canonicals.add(_strip_qualifier(pv.property_name))

    dropped_noise = 0
    for extraction, classification, filename in extractions:
        for pv in extraction.performance.values:
            # Drop catalog noise (per-plant tables, cross-product variants)
            # when the canonical property is already covered by an authoritative doc
            if _is_catalog_noise(pv.property_name):
                canon = _strip_qualifier(pv.property_name)
                if canon in authoritative_canonicals:
                    dropped_noise += 1
                    continue
                # Also drop if the doc itself is just a catalog with no auth coverage
                if classification.document_type == DocumentType.CATALOG:
                    dropped_noise += 1
                    continue
            key = pv.property_name.strip().lower()
            if key not in all_values:
                all_values[key] = []
            all_values[key].append((pv, classification.document_type, filename))

    if dropped_noise:
        logger.info(f"Performance filter: dropped {dropped_noise} catalog-noise entries (per-plant/cross-product)")

    merged_values = []
    for key, candidates in all_values.items():
        if len(candidates) == 1:
            merged_values.append(candidates[0][0])
        else:
            # Pick best by authority
            field_candidates = [
                (c[0].value, c[1], c[2]) for c in candidates
            ]
            best = _pick_best_field(
                field_candidates, PERFORMANCE_AUTHORITY,
                f"performance.{key}", conflicts,
            )
            # Use the first candidate's structure, replace value field
            winner = candidates[0][0].model_copy(update={"value": best})
            merged_values.append(winner)

    passport.performance.values = merged_values


def _merge_lifecycle(passport, extractions, conflicts) -> None:
    """Merge lifecycle data — A3 manufacturing + EPD stages."""
    authority = ENVIRONMENTAL_AUTHORITY

    # A3 manufacturing fields
    a3 = passport.lifecycle.a3_manufacturing
    for field_name in a3.model_fields:
        target_val = getattr(a3, field_name)
        if not isinstance(target_val, ExtractedField):
            # Handle nested (energy)
            if hasattr(target_val, "model_fields"):
                _merge_section_fields(
                    target_val, f"lifecycle.a3_manufacturing.{field_name}",
                    extractions, authority, conflicts,
                )
            continue

        candidates = []
        for extraction, classification, filename in extractions:
            src_a3 = extraction.lifecycle.a3_manufacturing
            if hasattr(src_a3, field_name):
                src_val = getattr(src_a3, field_name)
                if isinstance(src_val, ExtractedField):
                    candidates.append((src_val, classification.document_type, filename))

        if candidates:
            best = _pick_best_field(
                candidates, authority, f"lifecycle.a3.{field_name}", conflicts,
            )
            setattr(a3, field_name, best)

    # EPD stages — just collect all unique stages
    all_stages = {}
    for extraction, classification, filename in extractions:
        for stage in extraction.lifecycle.stages:
            code = stage.stage_code
            if code not in all_stages:
                all_stages[code] = stage
            # If we already have this stage, prefer the one from a higher-authority doc
            else:
                existing_rank = _authority_rank(
                    DocumentType.EPD, authority  # Assume existing came from EPD
                )
                new_rank = _authority_rank(classification.document_type, authority)
                if new_rank < existing_rank:
                    all_stages[code] = stage

    passport.lifecycle.stages = list(all_stages.values())


def _merge_composition_materials(passport, extractions) -> None:
    """
    Union materials from all documents, deduplicating by description, then
    drop hallucinated extras when authoritative data is available.

    Hallucination guard: when at least one material carries authoritative data
    (a quantity_per_product, percentage, or supplier — i.e. it came from a
    BoM or an EPD composition table), any other material that has NO such
    fields is treated as inferred-from-prose and dropped. This catches the
    common pattern where the AI lists the BoM correctly (4 materials with
    quantities) then adds 'Recycled fibers / Cork / Perlite' from the tech
    sheet's marketing prose.
    """
    seen: dict[str, object] = {}

    def _norm(s: object) -> str:
        if not s:
            return ""
        return str(s).strip().lower()

    def _ef_value(field):
        return field.value if isinstance(field, ExtractedField) else None

    def _has_authoritative_data(material) -> bool:
        if _ef_value(getattr(material, "quantity_per_product", None)) not in (None, "", 0):
            return True
        if _ef_value(getattr(material, "percentage", None)) not in (None, "", 0):
            return True
        suppliers = getattr(material, "suppliers", None) or []
        for s in suppliers:
            name = _ef_value(getattr(s, "name", None))
            addr = _ef_value(getattr(s, "address", None))
            if (name and str(name).strip() not in ("", "-")) or (addr and str(addr).strip() not in ("", "-")):
                return True
        return False

    for extraction, classification, filename in extractions:
        for material in extraction.composition.materials:
            desc_field = material.description
            desc = desc_field.value if isinstance(desc_field, ExtractedField) else None
            key = _norm(desc) or _norm(getattr(material, "id_code", None)) or _norm(material.material_id)
            if not key:
                continue
            if key not in seen:
                seen[key] = material

    materials = list(seen.values())
    # Hallucination filter
    quantified = [m for m in materials if _has_authoritative_data(m)]
    if quantified:
        kept = quantified
        dropped = [m for m in materials if not _has_authoritative_data(m)]
        if dropped:
            names = []
            for m in dropped:
                desc = _ef_value(getattr(m, "description", None))
                if desc:
                    names.append(str(desc))
            logger.info(
                f"Composition filter: dropped {len(dropped)} unquantified material(s) "
                f"({len(quantified)} authoritative remain) — likely AI inferred from prose: "
                f"{names}"
            )
        passport.composition.materials = kept
    else:
        passport.composition.materials = materials


def _merge_certifications(passport, extractions) -> None:
    """
    Union certification entries (product + company) from all documents.

    Deduplicate by (name, reference_number) so the same EPD/ISO/DECLARE
    cert isn't listed twice when it appears in multiple PDFs.
    """
    def _cert_key(cert) -> str:
        name = cert.name.value if isinstance(cert.name, ExtractedField) else None
        ref = cert.reference_number.value if isinstance(cert.reference_number, ExtractedField) else None
        return f"{(name or '').strip().lower()}|{(ref or '').strip().lower()}"

    for attr in ("product_certifications", "company_certifications"):
        seen: dict[str, object] = {}
        for extraction, classification, filename in extractions:
            certs = getattr(extraction.compliance, attr, []) or []
            for cert in certs:
                key = _cert_key(cert)
                if key in ("|", ""):
                    continue
                if key not in seen:
                    seen[key] = cert
        setattr(passport.compliance, attr, list(seen.values()))


def _build_merge_stats(passport, extractions, conflicts) -> MergeResult:
    """Build the MergeResult statistics."""
    confidence_dist = {"high": 0, "medium": 0, "low": 0}
    stats = {"filled": 0, "total": 0}
    _count_extracted_fields(passport, stats, confidence_dist)

    return MergeResult(
        documents_merged=[fn for _, _, fn in extractions],
        conflicts=conflicts,
        total_fields_filled=stats["filled"],
        total_fields=stats["total"],
        confidence_distribution=confidence_dist,
    )


def _count_extracted_fields(obj, stats: dict, dist: dict) -> None:
    """Recursively count ExtractedField instances in a model."""
    if isinstance(obj, ExtractedField):
        stats["total"] += 1
        if obj.is_filled:
            stats["filled"] += 1
        dist[obj.confidence.value] = dist.get(obj.confidence.value, 0) + 1
        return

    if hasattr(obj, "model_fields"):
        for field_name in obj.model_fields:
            val = getattr(obj, field_name)
            _count_extracted_fields(val, stats, dist)
    elif isinstance(obj, list):
        for item in obj:
            _count_extracted_fields(item, stats, dist)
