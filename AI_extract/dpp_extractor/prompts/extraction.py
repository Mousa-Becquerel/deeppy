"""
System prompts for Pass 2 — Per-document data extraction.

The extraction prompt is dynamically assembled based on:
  - Document type (DoP, TechnicalSheet, EPD, etc.)
  - Product family (DWS, MAS, etc.) → drives performance fields + process steps
"""

from ..ontology.enums import DocumentType, ProductFamily
from ..ontology.performance_registry import get_performance_fields
from ..ontology.manufacturing_registry import get_process_steps
from ..ontology.bom_template import get_bom_template


# ---------------------------------------------------------------------------
# Base extraction instructions (always included)
# ---------------------------------------------------------------------------

_BASE_INSTRUCTIONS = """\
You are an expert data extractor for construction-product technical documents.
Your task is to extract structured data from the provided PDF document and return it \
as a flat JSON object matching the output schema.

GENERAL RULES:
- Extract ONLY information explicitly stated in the document. Never infer or guess.
- Fill every field you can find data for. Set fields to null only if the information \
is truly not present in the document.
- For string fields, provide the extracted value directly as a plain string.
- For numeric fields (float), provide the number only (no units in the number field).
- If the document is in Italian, extract and translate field values to English where \
appropriate (e.g., product descriptions), but keep proper nouns, brand names, and \
standard references in their original form.
- Numbers: use dot as decimal separator, no thousand separators.
- Dates: use ISO format YYYY-MM-DD when possible.
- Be thorough: scan ALL pages of the document. Product info and manufacturer details \
are often on the first and last pages. Performance values may be in tables.
- Fields with enum/Literal types in the schema have predefined allowed values — \
the schema enforces valid choices, so just pick the closest match.
- product_family_code: leave null — it will be auto-mapped.

SAFETY QUESTIONS — answer in a context-aware way (Yes / No / n.a.):
The compliance.safety boolean fields ask whether the product CONTAINS / HAS / COMPLIES with \
specific substances or regulations. For each, follow this decision tree:
  1. The document explicitly states presence/absence → answer accordingly (Yes/No).
  2. The document is silent BUT the product family makes the answer obvious → answer based \
on common knowledge of the family. Examples:
       • A wood/aluminium/PVC window typically does NOT contain pentane (used as a \
blowing agent for foam) → "No".
       • A window/masonry product typically does NOT contain asbestos (banned in EU \
since 2005) → "No".
       • A typical construction product is RoHS-compliant unless it has electronic \
components → "Yes" only when relevant; "n.a." for non-electronic products.
       • CMR / SVHC / PFAS / heavy metals: if the document declares regulatory \
compliance with REACH and lists no SVHCs → "No". If genuinely unclear → "n.a.".
       • Child labor compliance: if the document mentions ISO certifications, \
EU manufacturing, or sustainability statements → "Yes". Otherwise "n.a." (don't \
assume "No" — manufacturers usually comply but might not state it).
       • VOC emission: thermal insulation, paints, adhesives, sealants → "Yes". \
Solid materials (glass, brick, metal) → "No". When unclear → "n.a.".
  3. Truly unknowable from the document and family → "n.a.".

Don't leave safety fields null — pick the most appropriate of the three values.
"""

# ---------------------------------------------------------------------------
# Document-type-specific instructions
# ---------------------------------------------------------------------------

_DOP_INSTRUCTIONS = """\

DOCUMENT TYPE: Declaration of Performance (DoP)
This document is a DoP issued under EU Construction Products Regulation.
Focus on extracting:
- DoP reference number and harmonized standard (e.g., EN 14351-1:2006+A2:2016)
- Notified body name and number
- CE marking information
- Product name, intended use, manufacturer details
- Manufacturer legal address AND manufacturing site address (NOT just the company \
  name — extract street, postal code, city, province)
- Production period / year of issue
- ALL declared performance values (these map to the Performance section)
- Factory Production Control (FPC) certificate reference
"""

_TECHNICAL_SHEET_INSTRUCTIONS = """\

DOCUMENT TYPE: Technical Data Sheet (Scheda Tecnica)
This is a product technical specification sheet.
Focus on extracting:
- Product name, model/code, manufacturer
- Physical dimensions (W × H or W × D × H, with units in mm or m) — look for \
  sections titled 'Dimensioni', 'Misure', 'Dimensions', 'Standard sizes'
- Weight (kg or kg/m²)
- Production date / year (anno produzione, year of issue)
- ALL technical/performance properties with their values and units
- Application/intended use descriptions
- Reference standards
- Material composition if mentioned
"""

_EPD_INSTRUCTIONS = """\

DOCUMENT TYPE: Environmental Product Declaration (EPD)
This is an EPD compliant with EN 15804.
Focus on extracting:
- EPD registration number, program operator, validity dates
- Functional unit and reference service life
- Product description and manufacturer
- LCA results per lifecycle stage (A1-A5, B1-B7, C1-C4, D):
  - GWP-total, GWP-fossil, GWP-biogenic, GWP-LULUC (kg CO2-eq)
  - ODP (kg CFC-11-eq), AP (mol H+-eq)
  - EP-freshwater (kg P-eq), EP-marine (kg N-eq)
  - POCP (kg NMVOC-eq)
  - ADP-minerals (kg Sb-eq), ADP-fossil (MJ)
  - WDP (m3 world-eq)
- Declared performance values if included
- Material composition / Bill of Materials if included
"""

_SDS_INSTRUCTIONS = """\

DOCUMENT TYPE: Safety Data Sheet (SDS)
This is a Safety Data Sheet under REACH regulation.
Focus on extracting:
- Product name and manufacturer
- Hazard classification (GHS/CLP)
- Composition / substance information
- Safety questions: CMR substances, SVHCs, PFAS, pentane, heavy metals, \
asbestos, flame retardants, VOC emissions, RoHS compliance
"""

_CERTIFICATE_INSTRUCTIONS = """\

DOCUMENT TYPE: Certificate
This is a certification document (ISO, CE, FPC, thermal, acoustic, fire, etc.).
Focus on extracting:
- Certificate name and type (e.g., ISO 9001, FPC, thermal conductivity test)
- Reference/registration number
- Issuing body / notified body
- Validity dates (issued, expires)
- Scope of certification
- Any declared performance values from test results
"""

_CATALOG_INSTRUCTIONS = """\

DOCUMENT TYPE: Product Catalog / Brochure / Technical Manual
This is commercial / reference material that typically documents MANY products
in a single PDF. You will receive a "TARGET PRODUCT" hint in the user message
identifying the ONE product the passport is for.

EXTRACT FREELY from the catalog:
- Manufacturer details (company name, address, website, email, phone, sale type)
- Company-level certifications (ISO 9001, ISO 14001, ISO 45001, etc.)
- The TARGET PRODUCT's commercial name, description, and intended use

DO NOT extract performance / composition / compliance data UNLESS the document
explicitly ties the value to the TARGET PRODUCT (by name, code, or dimension).

STRICT REJECTION RULES — these are mistakes you must not make:

  ✗ REJECT performance values labeled with a different product name than the
    target (e.g., if target is 'Porotherm BIO 35x25x19', REJECT values for
    'Porotherm BIO PLAN 45 T9', 'Porotherm Thermal T 15', 'BIO MOD Sonico 25',
    'Wall Force Compact', 'TERRACOAT', etc.).

  ✗ REJECT per-PLANT / per-FACTORY tables. Catalogs often show a single
    property measured across multiple production sites in a single table
    (e.g., a row 'Medium density' with columns for Bubano / Feltre / Terni /
    Gattinara plants). DO NOT extract one entry per plant. If the target
    product is from ONE specific plant, extract ONLY that plant's column.
    If no plant is identified for the target, OMIT the value entirely.

  ✗ REJECT range values that span multiple variants (e.g., 'fbk = 13 - 20
    N/mm²' covering several products in a series). Only extract a single
    point value clearly assigned to the target product.

  ✗ REJECT data sourced from sub-product accessories, ancillary products,
    finishes, or coatings even if they appear adjacent to the target's data.

CATALOGS ARE A LOW-PRIORITY SOURCE for technical data. The DoP, Certificate,
Technical Sheet, and EPD are the authoritative sources. Catalogs should only
ADD information the authoritative documents do not already provide, AND only
when that information is unambiguously about the target product.

If in doubt about whether a value applies to the target — OMIT IT.
"""

_DOC_TYPE_PROMPTS: dict[DocumentType, str] = {
    DocumentType.DOP: _DOP_INSTRUCTIONS,
    DocumentType.TECHNICAL_SHEET: _TECHNICAL_SHEET_INSTRUCTIONS,
    DocumentType.EPD: _EPD_INSTRUCTIONS,
    DocumentType.SDS: _SDS_INSTRUCTIONS,
    DocumentType.CERTIFICATE: _CERTIFICATE_INSTRUCTIONS,
    DocumentType.CATALOG: _CATALOG_INSTRUCTIONS,
}


# ---------------------------------------------------------------------------
# Dynamic performance fields prompt section
# ---------------------------------------------------------------------------

def _build_performance_prompt(family: ProductFamily) -> str:
    """Build the performance extraction section from the family registry."""
    fields = get_performance_fields(family)
    if not fields:
        return ""

    lines = [
        "",
        "PERFORMANCE PROPERTIES TO EXTRACT:",
        f"For this product family ({family.value}), extract these specific properties:",
        "",
    ]
    for i, f in enumerate(fields, 1):
        unit_str = f" [{f.unit}]" if f.unit else ""
        std_str = f" (test standard: {f.test_standard})" if f.test_standard else ""
        lines.append(f"  {i}. {f.name}{unit_str}{std_str}")

    lines.append("")
    lines.append(
        "For each property, extract the declared/tested value as a string, its unit, "
        "and the test standard reference if stated in the document. "
        "If a property is not mentioned in this document, omit it from the values list."
    )
    lines.append("")
    lines.append(
        "PROPERTY NAMES — use the EXACT canonical names from the list above. "
        "If the document provides multiple values for the same canonical property "
        "(e.g., one Uw value per window variant), include the variant qualifier in "
        "parentheses AFTER the canonical name. Examples: "
        "'Thermal transmittance (Uw) (window, 1 leaf)'; "
        "'Watertightness (French door)'; "
        "'Sound insulation (Rw) (glass)'. "
        "Do NOT invent new property names that are minor variations of canonical names."
    )
    lines.append("")
    lines.append(
        "CATEGORY — set the 'category' field on every performance value to ONE of: "
        "'Mechanical', 'Thermal', 'Acoustic', 'Fire', 'Durability', 'Environmental'. "
        "Use 'Other' ONLY as a last resort. Rules per category:"
    )
    lines.append("  Mechanical — load resistance, strength values, impact resistance, "
                 "burglary resistance, operating forces, pendulum, anti-effrazione, RC class")
    lines.append("  Thermal — Uw, Ug, Uf, Psi, lambda, conductivity, resistance, "
                 "solar factor (g), light transmittance, light reflectance, "
                 "temperature factor (fRsi). All optical/glazing properties go here.")
    lines.append("  Acoustic — Rw, sound insulation, sound absorption, dB values, "
                 "airborne / impact sound")
    lines.append("  Fire — Euroclass A1/A2/B/C/D/E/F, fire resistance class, reaction to fire, "
                 "smoke (s1/s2/s3), droplets (d0/d1/d2)")
    lines.append("  Durability — air permeability, watertightness, freeze-thaw cycles, "
                 "UV resistance, corrosion, chemical/biological resistance, "
                 "repeated opening/closing, water absorption, life expectancy, "
                 "vapor diffusion")
    lines.append("  Environmental — GWP, embodied energy/carbon, recycled content, "
                 "circularity index, water consumption, VOC emissions/content, "
                 "release of dangerous substances, biodegradable/recyclable percentages")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Dynamic Bill of Materials hint
# ---------------------------------------------------------------------------

def _build_bom_prompt(family: ProductFamily) -> str:
    """Build a BOM extraction hint listing typical materials for the family."""
    template = get_bom_template(family)
    if not template:
        return ""
    lines = [
        "",
        "BILL OF MATERIALS (composition):",
        f"For this product family ({family.value}), typical materials include:",
    ]
    for i, m in enumerate(template, 1):
        lines.append(f"  {i}. {m}")
    lines.append("")
    lines.append(
        "Extract any material/component you find in the document. The list above "
        "is a guide — extract what's actually declared, not what's expected. "
        "For each material, provide id_code (if any), description, unit, "
        "quantity_per_product, percentage, origin, and supplier info if available."
    )
    lines.append(
        "If a 'USER-PROVIDED BILL OF MATERIALS' section appears in the user message, "
        "use it as the AUTHORITATIVE composition data. Reconcile/enrich it with what "
        "you find in the PDFs, but don't invent materials not listed there unless the "
        "PDFs explicitly add new ones."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Dynamic manufacturing process steps prompt section
# ---------------------------------------------------------------------------

def _build_manufacturing_prompt(family: ProductFamily) -> str:
    """Build the A3 manufacturing extraction section from the family registry."""
    steps = get_process_steps(family)

    lines = [
        "",
        "A3 MANUFACTURING DATA:",
        "If this document contains manufacturing or production information, extract:",
        "- Reference year for production data",
        "- Total annual production volume",
        "- Process description",
        f"- Process steps (expected for this family: {', '.join(steps)})",
        "- Energy consumption: electrical (kWh/yr), thermal (Sm³/yr), renewable rates (%)",
        "- On-site PV production (kWh/yr)",
        "- Energy grid mix (fossil/renewable %)",
        "- Water use (m³/yr)",
        "- Packaging description",
        "- Waste production (material type + weight in kg)",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API: build the full extraction prompt
# ---------------------------------------------------------------------------

def build_extraction_prompt(
    doc_type: DocumentType,
    family: ProductFamily,
    document_name: str,
    user_bom_provided: bool = False,
) -> str:
    """
    Assemble the complete extraction system prompt for a specific document.

    Args:
        doc_type: Classified document type from Pass 1.
        family: Detected product family from Pass 1.
        document_name: Filename for source reference.

    Returns:
        Complete system prompt string.
    """
    parts = [_BASE_INSTRUCTIONS]

    # Document-type-specific instructions
    type_prompt = _DOC_TYPE_PROMPTS.get(doc_type, "")
    if type_prompt:
        parts.append(type_prompt)

    # Performance fields (relevant for DoP, TechnicalSheet, EPD, Certificate)
    if doc_type in (
        DocumentType.DOP, DocumentType.TECHNICAL_SHEET,
        DocumentType.EPD, DocumentType.CERTIFICATE,
    ):
        parts.append(_build_performance_prompt(family))

    # BOM hint — per ontology, composition data primarily comes from EPD or
    # user-uploaded BoM. When the user has uploaded a real BoM xlsx, we skip the
    # generic family template entirely (the user message will inject the actual
    # BoM as authoritative) to avoid confusing the AI with two BoM signals.
    if user_bom_provided:
        parts.append(
            "\nCOMPOSITION:\n"
            "A user-provided Bill of Materials is included in the user message. "
            "Treat it as the AUTHORITATIVE composition source. Do not invent additional "
            "materials from this document unless the document explicitly declares a "
            "material that isn't in the user's BoM (and is clearly part of the product)."
        )
    elif doc_type in (DocumentType.EPD, DocumentType.BOM):
        bom_section = _build_bom_prompt(family)
        if bom_section:
            parts.append(bom_section)
    else:
        # For non-EPD/BOM docs without a user BoM, instruct to NOT extract
        # composition unless the doc explicitly contains a BoM section.
        parts.append(
            "\nCOMPOSITION:\n"
            "Composition data should come from EPD documents or user-uploaded BoM files. "
            "For this document type, only fill composition.materials if the document "
            "contains an explicit Bill of Materials / sourcing table. Otherwise leave it empty."
        )

    # Manufacturing data (relevant for EPD, TechnicalSheet)
    if doc_type in (DocumentType.EPD, DocumentType.TECHNICAL_SHEET):
        parts.append(_build_manufacturing_prompt(family))

    # Final instruction
    parts.append(
        f'\nThe document filename is "{document_name}". '
        "Fill as many fields as possible from the document content. "
        "Do not leave fields null if the information exists anywhere in the document."
    )

    return "\n".join(parts)
