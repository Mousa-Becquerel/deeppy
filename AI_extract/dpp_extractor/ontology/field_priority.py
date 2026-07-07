"""
Per-field document priority registry.

Maps each DPP field to an ordered list of DocumentType (highest authority first),
based on the priority numbers in DeePPy_data_ontology.xlsx → Data_ontology sheet
(columns DoP, CE, Website, EPD, Technical data sheet).

When merging extracted values from multiple documents, the merger first checks if
the field has a specific priority list in this registry; if not, it falls back to
the section-level authority list defined in merge.py.
"""

from .enums import DocumentType


# ──────────────────────────────────────────────────────────────────────────
# Per-field document priority lists
# Order: highest authority first (DocumentType the field is most likely to come from)
# ──────────────────────────────────────────────────────────────────────────

FIELD_PRIORITY: dict[str, list[DocumentType]] = {
    # ─── Overview → Product Information ───────────────────────────────
    # Note: ontology priorities — DoP=1, CE=2, EPD=3, TechSheet=4, Website=5
    "overview.product_info.product_name": [
        DocumentType.DOP, DocumentType.EPD, DocumentType.TECHNICAL_SHEET, DocumentType.CATALOG,
    ],
    "overview.product_info.product_image": [
        DocumentType.EPD, DocumentType.TECHNICAL_SHEET, DocumentType.CATALOG,
    ],
    "overview.product_info.product_description": [
        DocumentType.EPD, DocumentType.TECHNICAL_SHEET, DocumentType.CATALOG,
    ],
    "overview.product_info.uid": [
        DocumentType.DOP,
    ],
    "overview.product_info.item_type": [
        DocumentType.DOP, DocumentType.EPD, DocumentType.TECHNICAL_SHEET,
    ],
    "overview.product_info.product_family": [
        DocumentType.DOP, DocumentType.EPD, DocumentType.TECHNICAL_SHEET,
    ],
    "overview.product_info.intended_use": [
        DocumentType.DOP, DocumentType.EPD, DocumentType.TECHNICAL_SHEET,
    ],
    "overview.product_info.functional_unit": [
        DocumentType.EPD, DocumentType.TECHNICAL_SHEET,
    ],
    "overview.product_info.standard_dimension": [
        DocumentType.EPD, DocumentType.TECHNICAL_SHEET,
    ],
    "overview.product_info.weight": [
        DocumentType.EPD, DocumentType.TECHNICAL_SHEET,
    ],
    # Per ontology: CE=1, DoP=2, EPD=3 — the certificate (CE) is the primary source
    "overview.product_info.production_period": [
        DocumentType.CERTIFICATE, DocumentType.DOP, DocumentType.EPD,
    ],

    # ─── Overview → Manufacturer ───────────────────────────────────────
    # Notes: DoP=1, Website=2, EPD=3, CE=4, TechSheet=5 → most reliable: DoP
    "overview.manufacturer.company_name": [
        DocumentType.DOP, DocumentType.CATALOG, DocumentType.EPD, DocumentType.TECHNICAL_SHEET,
    ],
    "overview.manufacturer.company_description": [
        DocumentType.CATALOG, DocumentType.TECHNICAL_SHEET,
    ],
    "overview.manufacturer.address": [
        DocumentType.DOP, DocumentType.CATALOG, DocumentType.EPD, DocumentType.TECHNICAL_SHEET,
    ],
    "overview.manufacturer.website": [
        DocumentType.CATALOG, DocumentType.TECHNICAL_SHEET,
    ],
    "overview.manufacturer.manufacturing_site": [
        DocumentType.DOP, DocumentType.CATALOG, DocumentType.EPD, DocumentType.TECHNICAL_SHEET,
    ],
    "overview.manufacturer.email": [
        DocumentType.CATALOG, DocumentType.TECHNICAL_SHEET,
    ],
    "overview.manufacturer.phone": [
        DocumentType.CATALOG, DocumentType.TECHNICAL_SHEET,
    ],

    # ─── Compliance → Declarations ─────────────────────────────────────
    "compliance.dop_reference": [DocumentType.DOP],
    "compliance.dop_standard": [DocumentType.DOP],
    "compliance.doc_reference": [DocumentType.DOP],
    "compliance.ce_marking": [DocumentType.CERTIFICATE],
    "compliance.quality_control": [DocumentType.TECHNICAL_SHEET, DocumentType.CERTIFICATE],
}


def get_field_priority(field_path: str) -> list[DocumentType] | None:
    """
    Return the priority list for a specific field, or None if no specific
    priority is defined (caller should fall back to section-level authority).

    Performance fields and lifecycle stages aren't listed individually since they
    follow the section-level authority for their category.
    """
    return FIELD_PRIORITY.get(field_path)
