"""
PDF page-level pre-filter for large documents.

Goal: when a user uploads a 10 MB catalog/manual, only the pages that
actually contain DPP-relevant data should be sent to Gemini. This cuts
extraction time, cost, and improves attention.

Strategy (text-based, no AI):
  1. Read text per page with pypdf
  2. Score each page against family-specific keyword lexicons
  3. Keep pages above threshold + a small safety margin (first/last page)
  4. Rebuild a slimmer PDF and return its bytes

If the PDF is small (<= MIN_PAGES_FOR_FILTER) or text extraction fails
(scanned PDF), the original bytes are returned unchanged.
"""

import io
import logging
import re
from pathlib import Path
from typing import Optional

from pypdf import PdfReader, PdfWriter

from ..ontology.enums import DocumentType, ProductFamily

logger = logging.getLogger(__name__)

# Filter only kicks in when the PDF has more pages than this.
# Below this, the savings aren't worth the risk of dropping relevant pages.
MIN_PAGES_FOR_FILTER = 15

# Always keep the first N and last N pages — covers cover, TOC, summaries.
ALWAYS_KEEP_FIRST = 2
ALWAYS_KEEP_LAST = 1

# Minimum keyword score to keep a page.
KEEP_THRESHOLD = 2

# Maximum number of pages to ever send to Gemini (safety cap).
MAX_PAGES_AFTER_FILTER = 60


# ─── Keyword lexicons ────────────────────────────────────────────────────
# Lower-cased substrings checked against each page's text.
# Hits accumulate the page's relevance score.

GENERIC_KEYWORDS: list[str] = [
    # Standards / declarations
    "en 1", "en 2", "en 3", "en 4", "en 5", "en 6", "en 7", "en 8", "en 9",
    "iso 9001", "iso 14001", "iso 45001", "iso 50001",
    "dop", "dichiarazione di prestazione", "declaration of performance",
    "ce marking", "marcatura ce", "cpr", "regulation 305/2011",
    "epd", "environmental product declaration",
    "sds", "scheda di sicurezza", "safety data sheet",
    "reach", "svhc", "rohs", "cmr", "pfas",
    # Manufacturer cues
    "p.iva", "vat", "piva", "fiscal code", "registrazione",
    "stabilimento", "plant", "manufacturing site",
    # Performance values
    "w/m", "w/(m", "m²·k", "m2k", "m^2", "kg/m", "n/mm", "kpa", "mpa",
    "db ", "db(", "db,", "decibel",
    "euroclass", "classe a", "classe b", "classe c", "classe d", "classe e", "classe f",
    "fire resistance", "reaction to fire", "reazione al fuoco",
    "thermal", "termica", "termico", "transmittance", "trasmittanza",
    "acoustic", "acustic", "sound", "sonor",
    "compressive", "tensile", "flexural", "flessione", "compress",
    # Environmental
    "gwp", "co2 eq", "co2eq", "kgco2", "embodied", "recycled content", "circular",
    # General product info
    "scheda tecnica", "technical data sheet", "datasheet",
    "intended use", "uso previsto",
    "functional unit", "unità funzionale",
    "dimensions", "dimensioni", "weight", "peso",
]

DWS_KEYWORDS: list[str] = GENERIC_KEYWORDS + [
    "uw ", "uw=", "u-value", "ug ", "ug=", "uf ", "uf=",
    "g value", "g-value", "solar factor",
    "watertightness", "tenuta", "permeability all'aria", "air permeability",
    "wind load", "carico vento", "resistance to wind",
    "frangisole", "shutter", "persiana", "anta", "telaio",
    "vetro", "glass", "lamina", "low-e", "vetrocamera",
]

MAS_KEYWORDS: list[str] = GENERIC_KEYWORDS + [
    "mattone", "brick", "block", "blocco",
    "porotherm", "biocotto", "laterizio",
    "freeze-thaw", "gelo-disgelo", "gelività",
    "compressive strength", "resistenza a compressione",
    "vapor diffusion", "diffusione vapore",
]

TIP_KEYWORDS: list[str] = GENERIC_KEYWORDS + [
    "thermal insulation", "isolante termico", "isolamento termico",
    "xps", "eps", "polystyrene", "polistirene",
    "mineral wool", "lana minerale", "rock wool",
    "lambda", "λ ", "conducibilità", "conductivity",
    "spessore", "thickness",
]

CEM_KEYWORDS: list[str] = GENERIC_KEYWORDS + [
    "cement", "cemento", "lime", "calce", "binder", "legante",
    "compressive strength", "resistenza", "classe di resistenza",
]

FAMILY_LEXICON: dict[ProductFamily, list[str]] = {
    ProductFamily.DWS: DWS_KEYWORDS,
    ProductFamily.MAS: MAS_KEYWORDS,
    ProductFamily.TIP: TIP_KEYWORDS,
    ProductFamily.CEM: CEM_KEYWORDS,
}


def _keywords_for(family: Optional[ProductFamily]) -> list[str]:
    if family is None:
        return GENERIC_KEYWORDS
    return FAMILY_LEXICON.get(family, GENERIC_KEYWORDS)


def _score_page(text: str, keywords: list[str]) -> int:
    """Count distinct keyword hits on a page."""
    if not text:
        return 0
    lower = text.lower()
    score = 0
    seen: set[str] = set()
    for kw in keywords:
        # Treat the keyword as found if its first word appears (cheaper than full substring)
        if kw in lower and kw not in seen:
            score += 1
            seen.add(kw)
    return score


def filter_pdf_pages(
    pdf_bytes: bytes,
    family: Optional[ProductFamily] = None,
    doc_type: Optional[DocumentType] = None,
    label: str = "",
) -> tuple[bytes, dict]:
    """
    Filter a PDF down to its relevant pages.

    Args:
        pdf_bytes: original PDF content
        family: product family hint (drives keyword choice)
        doc_type: document type hint (currently unused, reserved)
        label: filename for logs

    Returns:
        (filtered_bytes, metadata) where metadata is:
          {
            "original_pages": int,
            "kept_pages": int,
            "filtered": bool,
            "reason": str,    # why filtering was/wasn't applied
          }
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except Exception as e:
        logger.warning(f"[{label}] Cannot parse PDF for filtering ({e}); using original")
        return pdf_bytes, {"original_pages": 0, "kept_pages": 0, "filtered": False, "reason": f"parse_error: {e}"}

    n_pages = len(reader.pages)

    # Below threshold → don't filter, send full
    if n_pages <= MIN_PAGES_FOR_FILTER:
        return pdf_bytes, {"original_pages": n_pages, "kept_pages": n_pages, "filtered": False, "reason": "below_min_pages"}

    keywords = _keywords_for(family)

    # Score each page
    scores: list[int] = []
    has_any_text = False
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if text.strip():
            has_any_text = True
        scores.append(_score_page(text, keywords))

    # Scanned PDF (no extractable text) → fall back to original
    if not has_any_text:
        return pdf_bytes, {"original_pages": n_pages, "kept_pages": n_pages, "filtered": False, "reason": "no_text_extractable"}

    # Pick pages to keep
    keep_idx: set[int] = set()
    # Always keep first/last range
    for i in range(min(ALWAYS_KEEP_FIRST, n_pages)):
        keep_idx.add(i)
    for i in range(max(0, n_pages - ALWAYS_KEEP_LAST), n_pages):
        keep_idx.add(i)
    # Keep pages above threshold
    for i, sc in enumerate(scores):
        if sc >= KEEP_THRESHOLD:
            keep_idx.add(i)

    # Cap total pages — keep top-scoring ones if we exceed the cap
    if len(keep_idx) > MAX_PAGES_AFTER_FILTER:
        ranked = sorted(range(n_pages), key=lambda i: -scores[i])
        keep_idx = set(ranked[:MAX_PAGES_AFTER_FILTER])

    kept_pages = sorted(keep_idx)

    # If filtering would keep nearly all pages, just send the original
    if len(kept_pages) >= int(n_pages * 0.9):
        return pdf_bytes, {"original_pages": n_pages, "kept_pages": n_pages, "filtered": False, "reason": "no_significant_reduction"}

    # Rebuild slimmer PDF
    writer = PdfWriter()
    for i in kept_pages:
        writer.add_page(reader.pages[i])

    out = io.BytesIO()
    writer.write(out)
    filtered_bytes = out.getvalue()

    meta = {
        "original_pages": n_pages,
        "kept_pages": len(kept_pages),
        "filtered": True,
        "reason": "keyword_score",
        "kept_indices": kept_pages,
    }
    logger.info(
        f"[{label}] PDF filter: {n_pages} → {len(kept_pages)} pages "
        f"({len(pdf_bytes)//1024} KB → {len(filtered_bytes)//1024} KB)"
    )
    return filtered_bytes, meta
