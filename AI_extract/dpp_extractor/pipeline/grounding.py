"""
Post-merge grounding check — blank AI-fabricated values.

The problem: a client uploaded documents that did NOT contain any address for
the manufacturer, but the AI still returned `"Via Cavour 2 (MN)"` and marked
it high-confidence. The frontend renders that as a verified green field, and
the client reasonably assumes DeePPy read it from a document.

This module runs *after* merge and blanks (or downgrades) any string-typed
value on a known-risky field when that value cannot be located in the
concatenated normalized text of the source PDFs.

Scope: only fields where hallucinations are most damaging to trust —
manufacturer identity (name, address, phone, email, website, VAT-ish) and
compliance identifiers (DoP/CE/certification numbers). We do NOT gate:

  • product_name / product_description — legitimately paraphrased by the AI
  • numeric values — no useful substring test
  • enumerated fields — the schema constrains them already

Values that fail the check are blanked, confidence dropped to LOW, and a
`note` explains why so the user knows to enter it manually.
"""
from __future__ import annotations

import io
import logging
import re
import unicodedata
from pathlib import Path
from typing import Iterable, Optional

from ..models.common import ExtractedField, SourceReference
from ..models.passport import DigitalProductPassport
from ..ontology.enums import ConfidenceLevel

logger = logging.getLogger(__name__)


# Minimum overlap length below which "substring match" is meaningless (e.g. a
# 3-char company name would match half the corpus by accident). Values shorter
# than this get a pass — they're either enums (VAT country prefix, "Yes/No")
# or genuinely too short to protect.
_MIN_GUARDED_LENGTH = 6


# Manufacturer fields whose values are almost certainly present verbatim in
# a real document. Format: (attribute_name, human_label).
_MANUFACTURER_FIELDS = (
    ("company_name", "manufacturer.company_name"),
    ("address", "manufacturer.address"),
    ("website", "manufacturer.website"),
    ("manufacturing_site", "manufacturer.manufacturing_site"),
    ("email", "manufacturer.email"),
    ("phone", "manufacturer.phone"),
)

# Compliance identifiers — DoP numbers, certificate references, etc. Free-form
# strings (dop_standard, safety notes) are excluded because they're paraphrased.
_COMPLIANCE_FIELDS = (
    ("dop_reference", "compliance.dop_reference"),
    ("doc_reference", "compliance.doc_reference"),
    ("ce_marking", "compliance.ce_marking"),
    ("quality_control", "compliance.quality_control"),
)


# ─── Corpus extraction ─────────────────────────────────────────────────────

def build_corpus(file_paths: Iterable[Path]) -> str:
    """Concatenate normalized text from every uploaded PDF into one big
    haystack. Returns "" when no PDFs are readable.

    Uses pdfplumber because pypdf trips on the letter-spacing artifacts common
    in exported PDFs (turns "Article" into "Ar ticle"). Falls back to an empty
    string per-file on parse errors so one bad PDF doesn't defeat the whole
    check. Non-PDFs (xlsx, images) are skipped — the AI has no text-grounded
    reason to have populated a string field from them.
    """
    parts: list[str] = []
    for p in file_paths:
        p = Path(p)
        if p.suffix.lower() != ".pdf" or not p.exists():
            continue
        try:
            import pdfplumber  # lazy import — only needed for grounding
            with pdfplumber.open(p) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text() or ""
                    if txt:
                        parts.append(txt)
        except Exception as e:
            logger.warning(f"[grounding] Skipping {p.name}: {type(e).__name__}: {e}")
    return _normalize("\n".join(parts))


def _normalize(s: str) -> str:
    """Lower-case, strip diacritics, collapse whitespace, drop non-alnum.

    A hallucinated `"Via Cavour 2 (MN)"` normalizes to `"viacavour2mn"`. A
    real `"Via Emilia 42, 47921 Rimini (RN), Italia"` on p.1 of a DoP
    normalizes to `"viaemilia4247921riminirnitalia"`. Substring test against
    the corpus tells us honestly whether the value came from a document.
    """
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    ascii_only = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", ascii_only.lower())


# ─── Guarding ──────────────────────────────────────────────────────────────

def _blank(field: ExtractedField, reason: str, label: str) -> None:
    """Erase an unverifiable value in-place. Confidence drops to LOW and a
    note explains what happened so the user knows why the field is empty."""
    original = field.value
    field.value = None
    field.confidence = ConfidenceLevel.LOW
    field.source = None
    prior_note = (field.note or "").strip()
    guard_note = (
        f"Removed by grounding check: the AI value ({original!r}) could not "
        f"be located in any uploaded document. Enter the correct value manually."
    )
    field.note = f"{prior_note}\n{guard_note}".strip() if prior_note else guard_note
    logger.info(
        f"[grounding] Blanked {label} — value {original!r} not found in source corpus. Reason: {reason}"
    )


def _verify_string_field(
    field: Optional[ExtractedField], corpus: str, label: str,
) -> bool:
    """Check one field. Returns True when the field passed the check (or was
    exempt), False when it was blanked."""
    if field is None or not field.is_filled:
        return True
    value = field.value
    if not isinstance(value, str):
        # Non-string values (numbers, enums) are out of scope for this check.
        return True
    value_norm = _normalize(value)
    if len(value_norm) < _MIN_GUARDED_LENGTH:
        # Too short to reliably distinguish "in document" from "coincidence".
        return True
    if value_norm in corpus:
        return True

    # For values with multiple tokens (addresses, names), try a softer check:
    # do ≥70% of the tokens appear individually? This lets "Ediltech S.r.l."
    # survive a corpus that only has "Ediltech Srl" without the periods.
    tokens = [t for t in _normalize_tokens(value) if len(t) >= 4]
    if tokens:
        hits = sum(1 for t in tokens if t in corpus)
        if hits / len(tokens) >= 0.7:
            return True

    _blank(field, reason="not_in_corpus", label=label)
    return False


def _normalize_tokens(s: str) -> list[str]:
    """Same normalization as `_normalize` but keeps token boundaries — used
    for the fallback partial-match rule."""
    nfkd = unicodedata.normalize("NFKD", s)
    ascii_only = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", ascii_only.lower())


def verify_grounded_strings(
    passport: DigitalProductPassport, file_paths: Iterable[Path],
) -> dict:
    """Main entry — walks the guarded fields and blanks anything the corpus
    doesn't back up. Safe to call even when there are no PDFs (no-op).

    Returns a dict with counts for logging + observability.
    """
    corpus = build_corpus(file_paths)
    if not corpus:
        logger.info("[grounding] No corpus (0 readable PDFs); skipping grounding check")
        return {"checked": 0, "blanked": 0, "corpus_chars": 0}

    checked = 0
    blanked = 0

    mfr = getattr(passport.overview, "manufacturer", None)
    if mfr is not None:
        for attr, label in _MANUFACTURER_FIELDS:
            field = getattr(mfr, attr, None)
            checked += 1
            if not _verify_string_field(field, corpus, label):
                blanked += 1

    comp = getattr(passport, "compliance", None)
    if comp is not None:
        for attr, label in _COMPLIANCE_FIELDS:
            field = getattr(comp, attr, None)
            checked += 1
            if not _verify_string_field(field, corpus, label):
                blanked += 1

    logger.info(
        f"[grounding] Checked {checked} fields, blanked {blanked} unverifiable "
        f"({len(corpus)} chars corpus from {sum(1 for p in file_paths if Path(p).suffix.lower() == '.pdf')} PDFs)"
    )
    return {"checked": checked, "blanked": blanked, "corpus_chars": len(corpus)}
