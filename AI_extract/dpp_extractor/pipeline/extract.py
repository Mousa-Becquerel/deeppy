"""
Pass 2 — Per-document data extraction.

Uses Gemini structured output (output_type=SimpleExtractionOutput) like
the energy_bill_extractor pattern. The simplified model uses plain types
instead of ExtractedField wrappers, keeping the schema small enough for
Gemini's response_schema parameter. Results are then mapped to the full
ExtractedField model with confidence and source metadata.
"""

import logging
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel
from pydantic_ai import Agent, BinaryContent, RunContext, Tool

from ..models.classification import DocumentClassification
from ..models.common import ExtractedField, SourceReference
from ..models.extraction_output import DocumentExtractionOutput
from ..models.simple_extraction import SimpleExtractionOutput
from ..ontology.enums import DocumentType, ProductFamily, ConfidenceLevel
from ..preprocessing.bom_parser import bom_to_prompt_snippet
from ..preprocessing.pdf_filter import filter_pdf_pages
from ..prompts.extraction import build_extraction_prompt
from .classify import MEDIA_TYPES
from .model_factory import create_gemini_model

logger = logging.getLogger(__name__)


def _get_media_type(path: Path) -> str:
    ext = path.suffix.lower()
    media = MEDIA_TYPES.get(ext)
    if not media:
        raise ValueError(f"Unsupported file type: {ext}")
    return media


class ExtractionAgent:
    """Pass 2 agent — extracts structured data from a single classified document."""

    def __init__(self) -> None:
        self._model = create_gemini_model()
        logger.info("ExtractionAgent initialized")

    async def extract(
        self,
        file_path: Path,
        classification: DocumentClassification,
        website_url: Optional[str] = None,
        bom_data_list: Optional[list[dict]] = None,
        consensus_family: Optional[ProductFamily] = None,
        target_hint: Optional[dict] = None,
    ) -> DocumentExtractionOutput:
        file_path = Path(file_path)
        has_pdf = file_path.exists() and str(file_path) != "/dev/null"

        doc_type = classification.document_type
        per_doc_family = classification.product_family
        # The product family for the prompt should be the CONSENSUS (the actual product
        # the user is building a passport for), not the per-document family. A glass
        # DoP attached to a window upload should still be extracted with the window's
        # field set, not glass-product fields.
        family = consensus_family or per_doc_family or ProductFamily.OTH
        is_subcomponent = (
            per_doc_family is not None
            and consensus_family is not None
            and per_doc_family != consensus_family
        )

        doc_name = file_path.name if has_pdf else (website_url or "website")
        user_bom_provided = bool(bom_data_list)
        system_prompt = build_extraction_prompt(
            doc_type=doc_type,
            family=family,
            document_name=doc_name,
            user_bom_provided=user_bom_provided,
        )

        if is_subcomponent:
            system_prompt += (
                f"\n\nIMPORTANT — SUB-COMPONENT DOCUMENT:\n"
                f"This document was classified as belonging to '{per_doc_family.value}', "
                f"but the overall product is '{consensus_family.value}'. "
                f"This means the document is most likely about a SUB-COMPONENT or input material "
                f"(e.g., a glass pane DoP for a window assembly).\n"
                f"- DO NOT extract the document's manufacturer as the product's manufacturer.\n"
                f"- DO NOT extract the document's product name as the main product name.\n"
                f"- DO extract: composition/material info (this component is part of the BoM), "
                f"performance values that contribute to the assembly, and certifications.\n"
                f"- For overview fields (product_name, manufacturer, address, etc.), leave them null."
            )

        # Register web fetch tool when a website URL is provided
        tools = []
        if website_url:
            parsed = urlparse(website_url)
            allowed_domain = parsed.hostname or ""
            fetch_count = {"n": 0}

            async def fetch_webpage(ctx: RunContext, url: str) -> str:
                """Fetch a webpage and return its text content. Only allowed for the product domain."""
                target = urlparse(url)
                if target.hostname and target.hostname != allowed_domain:
                    return f"Error: fetching from {target.hostname} is not allowed. Only {allowed_domain} is permitted."
                if fetch_count["n"] >= 3:
                    return "Error: maximum number of web fetches (3) reached."
                fetch_count["n"] += 1
                logger.info(f"  Fetching webpage: {url}")
                try:
                    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
                        resp = await client.get(url, headers={"User-Agent": "DeePPy-Extractor/1.0"})
                        resp.raise_for_status()
                        # Return raw text (HTML) — Gemini can parse it
                        text = resp.text
                        # Truncate to avoid overwhelming the context
                        if len(text) > 50000:
                            text = text[:50000] + "\n\n[... truncated ...]"
                        logger.info(f"  Fetched {len(text)} chars from {url}")
                        return text
                except Exception as e:
                    logger.warning(f"  Failed to fetch {url}: {e}")
                    return f"Error fetching URL: {e}"

            tools.append(Tool(
                fetch_webpage,
                name="fetch_webpage",
                description=(
                    "Fetch a webpage URL and return its HTML/text content. "
                    "Use this ONLY to find manufacturer contact information that may be "
                    "missing from the PDFs: company description, email, phone, postal address, "
                    "physical website URL. "
                    "DO NOT use it to extract performance values, composition, certifications, "
                    "or DoP/CE references — those must come from the PDFs (DoP, EPD, "
                    "Technical Sheet, Certificate) which are the authoritative sources."
                ),
            ))
            logger.info(f"fetch_webpage tool enabled for domain: {allowed_domain}")

        # Only pass tools when actually defined — empty list can confuse some
        # provider/model combinations under pydantic-ai 1.87
        agent_kwargs = {
            "output_type": SimpleExtractionOutput,
            "system_prompt": system_prompt,
            # Deterministic generation so re-runs produce identical extractions
            # (no more flipping between 'Pth BIO inc' and 'Pth BIO inc 35-25/19 P 50')
            "model_settings": {"temperature": 0.0},
        }
        if tools:
            agent_kwargs["tools"] = tools
        agent = Agent(self._model, **agent_kwargs)

        if has_pdf:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            logger.info(
                f"Extracting from {file_path.name} "
                f"(type={doc_type.value}, family={family.value}, {file_size_mb:.1f} MB)"
                + (f", website: {website_url}" if website_url else "")
            )
        else:
            logger.info(f"Extracting from website only: {website_url}")

        # Build user message
        user_parts = []
        if has_pdf:
            media_type = _get_media_type(file_path)
            file_data = file_path.read_bytes()

            # For PDFs, run page-level filter to drop irrelevant pages from large docs
            filter_note = ""
            if media_type == "application/pdf":
                filtered_data, meta = filter_pdf_pages(
                    file_data,
                    family=family,
                    doc_type=doc_type,
                    label=file_path.name,
                )
                if meta.get("filtered"):
                    file_data = filtered_data
                    filter_note = (
                        f" (filtered: {meta['kept_pages']} of {meta['original_pages']} pages "
                        f"selected as relevant)"
                    )

            binary = BinaryContent(data=file_data, media_type=media_type)
            user_parts.append(f"Extract all structured data from this {doc_type.value} document: {file_path.name}{filter_note}")
            user_parts.append(binary)

        # For catalogs/brochures, anchor extraction to the target product if known
        if (
            doc_type == DocumentType.CATALOG
            and target_hint
            and any(target_hint.values())
        ):
            hint_lines = ["", "═══════════════════════════════════════════════════════════"]
            hint_lines.append("TARGET PRODUCT — STRICT FILTER")
            hint_lines.append("═══════════════════════════════════════════════════════════")
            hint_lines.append("")
            hint_lines.append("The product we are building a Digital Product Passport for is:")
            for label, key in (
                ("Product name", "product_name"),
                ("UID / code", "uid"),
                ("Dimension", "dimension"),
            ):
                v = target_hint.get(key)
                if v:
                    hint_lines.append(f"  • {label}: {v}")
            hint_lines.append("")
            hint_lines.append(
                "This brochure/catalog/manual documents MANY OTHER product variants in "
                "the same manufacturer's range, plus per-plant data tables, sub-product "
                "lines, accessory products, etc. THESE ARE NOT OUR TARGET."
            )
            hint_lines.append("")
            hint_lines.append("REJECTION RULES — apply STRICTLY to every value you consider:")
            hint_lines.append(
                "  ✗ REJECT any performance value labeled with a DIFFERENT product name "
                "than the TARGET PRODUCT above (e.g., reject rows for 'Porotherm BIO PLAN "
                "45 T9', 'Porotherm Thermal T 15', 'Porotherm BIO MOD Sonico 25', "
                "'TERRACOAT', 'Wall Force Compact', or any product that is clearly NOT "
                "the target product)."
            )
            hint_lines.append(
                "  ✗ REJECT per-PLANT tables that enumerate the same property for multiple "
                "production sites (e.g., a table with columns 'Bubano / Feltre / Terni / "
                "Gattinara' listing density per plant). Those are reference data, not "
                "this product's value."
            )
            hint_lines.append(
                "  ✗ REJECT performance values given as RANGES across multiple variants "
                "(e.g., 'fbk = 13 - 20 N/mm²' covering several products) UNLESS the "
                "document explicitly states the target product's value is at one specific "
                "endpoint of that range."
            )
            hint_lines.append(
                "  ✓ ACCEPT only values explicitly tied to the target product's name, "
                "code, or dimension — typically found in a dedicated product page, "
                "datasheet card, or labeled column for that variant."
            )
            hint_lines.append("")
            hint_lines.append(
                "If a value cannot be unambiguously tied to the target product, OMIT it. "
                "Better to extract fewer correct values than many ambiguous ones."
            )
            hint_lines.append("")
            hint_lines.append(
                "For Manufacturer contact info (company name, address, email, phone, "
                "website, description, sale_type) and Company-level certifications "
                "(ISO 9001, ISO 14001, ISO 45001) you MAY extract from anywhere in the "
                "catalog — those apply to the whole brand."
            )
            hint_lines.append("═══════════════════════════════════════════════════════════")
            user_parts.append("\n".join(hint_lines))

        # Inject user-provided BoM as authoritative composition context
        if bom_data_list:
            for bom in bom_data_list:
                snippet = bom_to_prompt_snippet(bom)
                if snippet:
                    user_parts.append(snippet)

        if website_url:
            if has_pdf:
                user_parts.append(
                    f"\nA manufacturer webpage is also available at: {website_url}\n"
                    "Use fetch_webpage to retrieve it ONLY if any of these fields are not "
                    "already declared in the PDF:\n"
                    "  • overview.manufacturer.company_description\n"
                    "  • overview.manufacturer.email\n"
                    "  • overview.manufacturer.phone\n"
                    "  • overview.manufacturer.website\n"
                    "  • overview.manufacturer.address (postal HQ)\n"
                    "  • overview.manufacturer.sale_type (direct sale vs retailers)\n"
                    "DO NOT use the website for performance values, composition (BoM), "
                    "DoP/CE references, certifications, or any technical product spec — "
                    "those MUST come from the PDF documents which are authoritative."
                )
            else:
                user_parts.append(
                    f"No PDF was uploaded. Fetch the manufacturer website at {website_url} "
                    "and extract ONLY manufacturer contact information: company_name, "
                    "company_description, email, phone, address, website, sale_type. "
                    "Leave performance, composition, compliance, and lifecycle fields null — "
                    "those require formal documents (DoP, EPD, Tech Sheet) that aren't provided."
                )

        result = await agent.run(user_parts)

        simple = result.output
        logger.info(f"Extraction complete for {file_path.name}")

        # Debug: log what Gemini returned for overview
        pi = simple.overview.product_info
        mf = simple.overview.manufacturer
        logger.info(f"  product_name={pi.product_name!r}, uid={pi.uid!r}, item_type={pi.item_type!r}")
        logger.info(f"  description={pi.product_description!r}")
        logger.info(f"  company={mf.company_name!r}, address={mf.address!r}, website={mf.website!r}")
        logger.info(f"  performance values count={len(simple.performance.values)}")
        logger.info(f"  certifications count={len(simple.compliance.product_certifications)}")
        logger.info(f"  materials count={len(simple.composition.materials)}")

        # Map simplified output → full ExtractedField model.
        # Pass consensus_family so the product's family on the passport is correct
        # (and not the per-document family from a sub-component).
        output = _map_to_extraction_output(
            simple, file_path.name, doc_type, classification, consensus_family,
        )
        return output


# ---------------------------------------------------------------------------
# Mapping: SimpleExtractionOutput → DocumentExtractionOutput
# ---------------------------------------------------------------------------

def _make_field(
    value,
    doc_name: str,
    doc_type: DocumentType = None,
    source_family: Optional[ProductFamily] = None,
) -> ExtractedField:
    """Create an ExtractedField from a plain value."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return ExtractedField(
            value=None,
            confidence=ConfidenceLevel.LOW,
            source=None,
            note=None,
        )
    return ExtractedField(
        value=value if isinstance(value, str) else str(value),
        confidence=ConfidenceLevel.HIGH,
        source=SourceReference(
            document_name=doc_name,
            document_type=doc_type,
            source_family=source_family,
        ),
        note=None,
    )


_FLOAT_RE = re.compile(r"-?\d+(?:[\.,]\d+)?")


def _coerce_float(value) -> Optional[float]:
    """Parse a leading number out of a string like '639.6 kg' or '10%'.

    Returns None if no parseable number is found. Comma decimals (0,42)
    are normalized to dot decimals (0.42).
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s:
        return None
    m = _FLOAT_RE.search(s.replace(",", "."))
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def _make_float_field(
    value,
    doc_name: str,
    doc_type: DocumentType = None,
    source_family: Optional[ProductFamily] = None,
) -> ExtractedField:
    """Create an ExtractedField[float] from a plain value."""
    parsed = _coerce_float(value)
    if parsed is None:
        return ExtractedField(value=None, confidence=ConfidenceLevel.LOW)
    return ExtractedField(
        value=parsed,
        confidence=ConfidenceLevel.HIGH,
        source=SourceReference(
            document_name=doc_name,
            document_type=doc_type,
            source_family=source_family,
        ),
    )


def _map_to_extraction_output(
    simple: SimpleExtractionOutput,
    doc_name: str,
    doc_type: DocumentType,
    classification: "DocumentClassification | None" = None,
    consensus_family: Optional[ProductFamily] = None,
) -> DocumentExtractionOutput:
    """Convert SimpleExtractionOutput → DocumentExtractionOutput with ExtractedField wrappers."""
    from ..models.overview import OverviewSection, ProductInfo, Manufacturer
    from ..models.performance import PerformanceSection, PerformanceValue
    from ..models.compliance import ComplianceSection, SafetyInfo, CertificationEntry
    from ..models.composition import CompositionSection, MaterialEntry
    from ..models.lifecycle import LifecycleSection, LifecycleStage, A3Manufacturing, ManufacturingEnergy
    from ..ontology.enums import PerformanceCategory, PRODUCT_FAMILY_CODES
    from ..ontology.family_defaults import get_default_functional_unit, get_default_item_type

    # The source_family records WHERE the data came from (the per-doc classification).
    # Merge will compare it against the consensus to detect sub-component contamination.
    src_family = classification.product_family if classification else None
    f = lambda v: _make_field(v, doc_name, doc_type, src_family)
    ff = lambda v: _make_float_field(v, doc_name, doc_type, src_family)

    def f_default(extracted_value, default_value, note):
        """Use extracted value if present, otherwise apply smart default with MEDIUM confidence."""
        if extracted_value:
            return f(extracted_value)
        if default_value:
            return ExtractedField(
                value=default_value,
                confidence=ConfidenceLevel.MEDIUM,
                # Stamp source_family so the merge filter can drop sub-component
                # default values (e.g., a glass DoP shouldn't dictate the window's item_type).
                source=SourceReference(
                    document_name=doc_name,
                    document_type=doc_type,
                    source_family=src_family,
                ),
                note=note,
            )
        return f(None)

    # Overview
    pi = simple.overview.product_info
    mf = simple.overview.manufacturer

    # Product family on the passport = the CONSENSUS family (the actual product
    # the user is building a passport for). The per-document classification family
    # is only used as `source_family` metadata, not as the product's identity.
    # Falls back to per-doc classification if no consensus passed, then to AI's guess.
    family_enum = consensus_family or (classification.product_family if classification else None)
    if family_enum is not None:
        family_name = family_enum.value  # full name from enum
        family_code = family_enum.name   # short code (DWS, MAS, etc.)
    else:
        family_name = pi.product_family
        family_code = PRODUCT_FAMILY_CODES.get(pi.product_family or "") or pi.product_family_code

    # Smart defaults based on product family
    default_item_type = get_default_item_type(family_enum) if family_enum else "Product"
    default_func_unit = get_default_functional_unit(family_enum) if family_enum else None

    overview = OverviewSection(
        product_info=ProductInfo(
            product_name=f(pi.product_name),
            product_description=f(pi.product_description),
            uid=f(pi.uid),
            item_type=f_default(pi.item_type, default_item_type, f"Default for {family_code} family. Please confirm."),
            product_family=f(family_name),
            product_family_code=f(family_code),
            intended_use=f(pi.intended_use),
            serial_number=f(pi.serial_number),
            batch_number=f(pi.batch_number),
            gtin=f(pi.gtin),
            functional_unit=f_default(pi.functional_unit, default_func_unit, f"Default for {family_code} family. Please confirm."),
            standard_dimension=f(pi.standard_dimension),
            weight=f(pi.weight),
            production_period=f(pi.production_period),
        ),
        manufacturer=Manufacturer(
            company_name=f(mf.company_name),
            company_description=f(mf.company_description),
            address=f(mf.address),
            website=f(mf.website),
            manufacturing_site=f(mf.manufacturing_site),
            email=f(mf.email),
            phone=f(mf.phone),
            sale_type=f(mf.sale_type),
        ),
    )

    # Performance — normalize AI-returned names against the ontology canonical list.
    # The AI tends to expand canonical names with variant qualifiers (e.g.,
    # "Thermal transmittance (Uw) - Window 1 leaf"). We restore the canonical
    # name for grouping, and parenthetically append the variant so the value
    # remains distinct from sibling variants.
    from ..ontology.performance_normalizer import normalize_property_name
    perf_target_family = family_enum or ProductFamily.OTH
    perf_values = []
    for pv in simple.performance.values:
        norm = normalize_property_name(pv.property_name, perf_target_family, pv.category)
        # Build the display name: canonical, plus variant in parentheses if present.
        # If the AI's raw name was already short and matched cleanly, we keep just canonical.
        if norm.variant and norm.variant.lower() not in norm.canonical.lower():
            display_name = f"{norm.canonical} ({norm.variant})"
        else:
            display_name = norm.canonical
        # Use the canonical's ontology category when we matched; otherwise trust the AI
        category = norm.category if norm.matched else (
            PerformanceCategory(pv.category) if pv.category in PerformanceCategory._value2member_map_
            else PerformanceCategory.OTHER
        )
        perf_values.append(PerformanceValue(
            property_name=display_name,
            category=category,
            value=f(pv.value),
            unit=pv.unit,
            test_standard=pv.test_standard,
        ))
    # Inject controlled fire/UV resistance as performance values if present
    if simple.performance.fire_resistance:
        perf_values.append(PerformanceValue(
            property_name="Fire resistance classification",
            category=PerformanceCategory.FIRE,
            value=f(simple.performance.fire_resistance),
            unit="Euroclass",
        ))
    if simple.performance.uv_resistance:
        perf_values.append(PerformanceValue(
            property_name="UV resistance",
            category=PerformanceCategory.DURABILITY,
            value=f(simple.performance.uv_resistance),
            unit="Category",
        ))
    performance = PerformanceSection(values=perf_values)

    # Compliance
    sc = simple.compliance
    sf = sc.safety
    compliance = ComplianceSection(
        dop_reference=f(sc.dop_reference),
        dop_standard=f(sc.dop_standard),
        doc_reference=f(sc.doc_reference),
        ce_marking=f(sc.ce_marking),
        quality_control=f(sc.quality_control),
        safety=SafetyInfo(
            contains_cmrs=f(sf.contains_cmrs),
            contains_svhcs=f(sf.contains_svhcs),
            contains_pentane=f(sf.contains_pentane),
            contains_pfas=f(sf.contains_pfas),
            has_flame_retardancy=f(sf.has_flame_retardancy),
            complies_rohs=f(sf.complies_rohs),
            produces_voc=f(sf.produces_voc),
            contains_heavy_metals=f(sf.contains_heavy_metals),
            contains_asbestos=f(sf.contains_asbestos),
            complies_child_labor=f(sf.complies_child_labor),
            other_declaration=f(sf.other_declaration),
        ),
        product_certifications=[
            CertificationEntry(
                name=f(c.name), reference_number=f(c.reference_number),
                issuing_body=f(c.issuing_body), valid_until=f(c.valid_until), scope=f(c.scope),
            ) for c in sc.product_certifications
        ],
        company_certifications=[
            CertificationEntry(
                name=f(c.name), reference_number=f(c.reference_number),
                issuing_body=f(c.issuing_body), valid_until=f(c.valid_until), scope=f(c.scope),
            ) for c in sc.company_certifications
        ],
        other_labels=f(sc.other_labels),
    )

    # Composition
    from ..models.composition import SupplierData
    materials = []
    for m in simple.composition.materials:
        suppliers = []
        for s in (m.suppliers or []):
            suppliers.append(SupplierData(
                name=f(s.name),
                address=f(s.address),
                transport_method=f(s.transport_method),
                eu_vehicle_class=f(s.eu_vehicle_class),
                distance_km=ff(s.distance_km),
            ))
        materials.append(MaterialEntry(
            material_id=m.material_id or f"Material#{len(materials)+1}",
            description=f(m.description),
            unit=f(m.unit),
            quantity_per_product=ff(m.quantity),
            percentage=ff(m.percentage),
            origin=f(m.origin),
            recyclable=f(m.recyclable),
            suppliers=suppliers,
        ))
    composition = CompositionSection(materials=materials)

    # Lifecycle
    stages = []
    # Per ontology, lifecycle (A1–C4) is "to be completed manually". Any AI
    # extraction here is a SUGGESTION — downgrade confidence and add a note so
    # the user reviews each value rather than trusting it as auto-extracted.
    _lifecycle_note = "Lifecycle data requires manual review (per ontology)."

    def _suggest(field: ExtractedField) -> ExtractedField:
        """Downgrade an extracted lifecycle field to MEDIUM with a manual-review note."""
        if not field.is_filled:
            return field
        return field.model_copy(update={
            "confidence": ConfidenceLevel.MEDIUM,
            "note": _lifecycle_note if not field.note else field.note,
        })

    for s in simple.lifecycle.stages:
        stages.append(LifecycleStage(
            stage_code=s.stage_code,
            gwp_total=_suggest(ff(s.gwp_total)), gwp_fossil=_suggest(ff(s.gwp_fossil)),
            gwp_biogenic=_suggest(ff(s.gwp_biogenic)), odp=_suggest(ff(s.odp)), ap=_suggest(ff(s.ap)),
            ep_freshwater=_suggest(ff(s.ep_freshwater)), ep_marine=_suggest(ff(s.ep_marine)),
            pocp=_suggest(ff(s.pocp)), adp_minerals=_suggest(ff(s.adp_minerals)),
            adp_fossil=_suggest(ff(s.adp_fossil)), wdp=_suggest(ff(s.wdp)),
        ))
    lifecycle = LifecycleSection(
        a3_manufacturing=A3Manufacturing(
            reference_year=_suggest(f(simple.lifecycle.reference_year)),
            process_description=_suggest(f(simple.lifecycle.process_description)),
        ),
        stages=stages,
    )

    return DocumentExtractionOutput(
        overview=overview,
        performance=performance,
        compliance=compliance,
        composition=composition,
        lifecycle=lifecycle,
    )
