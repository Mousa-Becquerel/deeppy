"""
Post-extraction passes that don't require AI — they derive structured data
from the classification results + uploaded filenames.

Per the ontology Notes column:
  - DoP / DoC / CE / Quality fields are "Uploaded by user, check if present"
  - Documents section entries are "Added docs, repository folder for downloading"

These shouldn't burn AI tokens. We populate them deterministically from the list
of source documents the orchestrator already has.
"""

import logging
import re
from pathlib import Path
from typing import Optional

from ..models.common import ExtractedField, SourceReference
from ..models.classification import DocumentClassification
from ..models.documents import DocumentReference
from ..models.passport import DigitalProductPassport
from ..ontology.enums import DocumentType, ConfidenceLevel

logger = logging.getLogger(__name__)


# ─── Compliance presence detection ────────────────────────────────────────

def populate_compliance_presence(
    passport: DigitalProductPassport,
    classifications: list[DocumentClassification],
    filenames: list[str],
) -> None:
    """
    Mark DoP / DoC / CE / Quality as present when the user uploaded a matching doc.

    The ontology says these are 'Uploaded by user, check if present' — i.e. they're
    booleans whose truth depends on whether a corresponding PDF was attached.
    The reference number, if any, comes from AI extraction (we don't overwrite
    a non-empty value with a presence flag).

    We prefer documents whose family matches the passport's product family — that way
    a glass-DoP doesn't win over a window-DoP for a window passport.
    """
    pairs = list(zip(classifications, filenames))
    consensus_family = passport.metadata.product_family if passport.metadata else None

    def _set_presence(target_field: ExtractedField, doc_type: DocumentType, label: str):
        # Don't overwrite an actually-extracted reference number
        if target_field.is_filled:
            return
        # Two-pass: first try to find a doc matching consensus family, then any doc
        matches = [(cls, fn) for cls, fn in pairs if cls and cls.document_type == doc_type]
        if not matches:
            return
        # Prefer the doc whose family matches consensus
        preferred = [
            (cls, fn) for cls, fn in matches
            if consensus_family is None
            or cls.product_family is None
            or cls.product_family == consensus_family
        ]
        chosen = preferred[0] if preferred else matches[0]
        cls, fn = chosen
        target_field.value = "Yes"
        target_field.confidence = ConfidenceLevel.HIGH
        target_field.source = SourceReference(
            document_name=fn,
            document_type=doc_type,
            source_family=cls.product_family,
        )
        target_field.note = f"{label} document uploaded"

    _set_presence(passport.compliance.dop_reference, DocumentType.DOP, "DoP")
    _set_presence(passport.compliance.doc_reference, DocumentType.DOP, "DoC")  # DoC reuses DOP type if present
    _set_presence(passport.compliance.ce_marking, DocumentType.CERTIFICATE, "CE certificate")
    _set_presence(passport.compliance.quality_control, DocumentType.CERTIFICATE, "Quality control certificate")


# ─── Documents section auto-linking ───────────────────────────────────────

# Filename keyword → documents.* slot
_FILENAME_TO_SLOT: list[tuple[tuple[str, ...], str]] = [
    # Most specific first — order matters
    (("manutenzione", "maintenance", "repair", "riparazione"),       "method_statement_maintenance"),
    (("installazione", "installation", "posa", "montaggio", "fitting"), "method_statement_installation"),
    (("smontaggio", "dismantling", "fine vita", "end of life", "eol", "demolizione"), "method_statement_dismantling"),
    (("sostituzione", "replacement", "refurbish", "ripristino"),     "method_statement_replacement"),
    (("scheda tecnica", "technical sheet", "datasheet", "data sheet"), "technical_data_sheet"),
    (("brochure", "catalog", "catalogo", "depliant"),                "brochure"),
]

# File extension → documents.* slot (used when classification doesn't help)
_EXT_TO_SLOT: dict[str, str] = {
    ".dwg": "drawing_2d",
    ".dxf": "drawing_2d",
    ".ifc": "drawing_3d",
    ".obj": "drawing_3d",
    ".step": "drawing_3d",
    ".stp": "drawing_3d",
    ".rvt": "drawing_3d",
    ".skp": "drawing_3d",
}

# DocumentType → default slot (when filename keyword doesn't match)
_TYPE_TO_SLOT: dict[DocumentType, str] = {
    DocumentType.TECHNICAL_SHEET: "technical_data_sheet",
    DocumentType.METHOD_STATEMENT: "method_statement_installation",  # generic fallback
    DocumentType.CATALOG: "brochure",
    DocumentType.DRAWING: "drawing_2d",
}


def _slot_for_document(filename: str, classification: Optional[DocumentClassification]) -> Optional[str]:
    """Return the documents.* attribute name to attach this file to, or None."""
    fname_lower = filename.lower()

    # 1. Filename keyword wins (most specific)
    for keywords, slot in _FILENAME_TO_SLOT:
        if any(kw in fname_lower for kw in keywords):
            return slot

    # 2. File extension (DWG / IFC / etc.)
    ext = Path(filename).suffix.lower()
    if ext in _EXT_TO_SLOT:
        return _EXT_TO_SLOT[ext]

    # 3. DocumentType from classification
    if classification and classification.document_type in _TYPE_TO_SLOT:
        return _TYPE_TO_SLOT[classification.document_type]

    return None


def populate_documents_section(
    passport: DigitalProductPassport,
    classifications: list[DocumentClassification],
    filenames: list[str],
) -> None:
    """
    Auto-link uploaded documents to the right documents.* slot based on
    filename keywords + classification.

    Each uploaded file is attached to AT MOST one slot (the most specific match).
    DoP / CE / EPD / Catalog / SDS files don't get attached here — they live in
    compliance.dop_reference / ce_marking / etc., or in their own dedicated logic.
    """
    SKIP_TYPES = {DocumentType.DOP, DocumentType.SDS}  # not Documents-section material
    docs = passport.documents
    attached_count = 0

    for cls, fn in zip(classifications, filenames):
        if cls and cls.document_type in SKIP_TYPES:
            continue
        slot = _slot_for_document(fn, cls)
        if not slot:
            continue
        if not hasattr(docs, slot):
            continue
        target_list = getattr(docs, slot)
        if any(d.filename == fn for d in target_list):
            continue  # already attached
        target_list.append(DocumentReference(filename=fn))
        attached_count += 1

    if attached_count:
        logger.info(f"Auto-linked {attached_count} files to Documents section")


# ─── Multi-variant product_name cleanup ───────────────────────────────────

# Filename noise stripped before matching against extracted variants.
_BOM_FILENAME_PREFIXES = (
    "bom ", "bom_", "bom-",
    "bill of materials", "distinta base", "distinta-base",
)
_PRODUCT_DOC_PREFIXES = (
    "report epd ", "report epd_",
    "epd ", "epd_",
    "dop ", "doc ", "dop_", "doc_",
    "scheda tecnica ", "technical sheet ", "datasheet ",
    "manuale ", "manual ",
    "dich.prestazioni ",  # Italian Declaration-of-Performance prefix
)


def _strip_doc_prefix(stem: str) -> str:
    """Drop document-type prefixes from a filename stem so what's left is
    closer to a product name. Case-insensitive, longest-match first."""
    low = stem.lower()
    for pref in sorted(_BOM_FILENAME_PREFIXES + _PRODUCT_DOC_PREFIXES, key=len, reverse=True):
        if low.startswith(pref):
            return stem[len(pref):].strip(" _-")
    return stem


def _tokens(s: str) -> set[str]:
    """Normalized token set for fuzzy matching."""
    s = re.sub(r"[^a-z0-9]+", " ", (s or "").lower())
    return {t for t in s.split() if len(t) >= 2}


def _target_skus_from_filenames(
    bom_data_list: Optional[list[dict]],
    filenames: list[str],
) -> list[str]:
    """Derive likely target-SKU strings from filenames in priority order:

      1. BoM source_file (BoM is per-SKU by definition — highest signal)
      2. EPD / DoP filenames (single-product authoritative docs)
    """
    out: list[str] = []
    if bom_data_list:
        for bom in bom_data_list:
            src = (bom or {}).get("source_file")
            if src:
                stem = Path(src).stem
                cleaned = _strip_doc_prefix(stem)
                if cleaned:
                    out.append(cleaned)
    # EPD/DoP filenames as secondary signal
    for fn in filenames:
        low = fn.lower()
        if any(k in low for k in ("epd", "dop", "dich.prestazioni", "dichiarazione")):
            stem = Path(fn).stem
            cleaned = _strip_doc_prefix(stem)
            if cleaned and cleaned not in out:
                out.append(cleaned)
    return out


def simplify_multi_variant_product_name(
    passport: DigitalProductPassport,
    bom_data_list: Optional[list[dict]],
    filenames: list[str],
) -> None:
    """Collapse a comma-separated list of variants in `product_name` to the
    single SKU best matched by attached BoM/EPD/DoP filenames.

    Symptom we're fixing: a user manual or catalog lists every SKU in the
    product range, so the AI returns `"VariantA, VariantB, VariantC, ..."`
    — when the user clearly meant just one of them (the one they uploaded
    a BoM/EPD for).

    No-op when:
      • product_name is empty
      • product_name has no comma (already a single name)
      • no BoM/EPD filename gives us a target SKU to align with
      • no variant is a confident match for the target
    """
    try:
        pi = passport.overview.product_info
    except AttributeError:
        return
    field = pi.product_name
    if not field or not field.is_filled:
        return
    raw = str(field.value or "")
    if "," not in raw:
        return  # already a single name

    candidates = [c.strip() for c in raw.split(",") if c.strip()]
    if len(candidates) <= 1:
        return

    targets = _target_skus_from_filenames(bom_data_list, filenames)
    if not targets:
        logger.info(
            f"product_name has {len(candidates)} variants but no BoM/EPD "
            "filename to disambiguate — leaving as-is"
        )
        return

    # Score each candidate against each target by token-overlap (Jaccard).
    target_token_sets = [_tokens(t) for t in targets]
    best_score = 0.0
    best_candidate: Optional[str] = None
    best_target: Optional[str] = None
    for cand in candidates:
        c_tokens = _tokens(cand)
        if not c_tokens:
            continue
        for t_tokens, t_raw in zip(target_token_sets, targets):
            if not t_tokens:
                continue
            overlap = c_tokens & t_tokens
            if not overlap:
                continue
            score = len(overlap) / len(c_tokens | t_tokens)
            # Require at least one numeric/identifier-like token in the overlap
            # so "Latemar Motore 230V" beats "Latemar Molla" against a "Motore 230V" target.
            if score > best_score:
                best_score = score
                best_candidate = cand
                best_target = t_raw

    # Threshold: at least 30% Jaccard. Below that we don't trust the match
    # and leave the user-facing field unchanged.
    if best_candidate and best_score >= 0.3:
        logger.info(
            f"Collapsed multi-variant product_name "
            f"({len(candidates)} variants → {best_candidate!r}, "
            f"matched against {best_target!r} with score {best_score:.2f})"
        )
        field.value = best_candidate
        existing_note = field.note or ""
        added = (
            f"Selected from {len(candidates)} variants listed in the source "
            f"documents, aligned with the attached BoM/EPD filename."
        )
        field.note = f"{existing_note} {added}".strip() if existing_note else added
    else:
        logger.info(
            f"product_name has {len(candidates)} variants but none confidently "
            f"matched targets {targets} (best score {best_score:.2f}) — leaving as-is"
        )
