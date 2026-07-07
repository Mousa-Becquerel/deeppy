"""
Simplified extraction model for Gemini structured output.

Uses plain types (str, float, Optional) instead of ExtractedField wrappers.
This keeps the schema small enough for Gemini's response_schema parameter.
After extraction, values are mapped to ExtractedField with confidence/source metadata.

Controlled fields use Literal types so Gemini's structured output enforces
valid values from the predefined lists (from DeePPy_data_ontology.xlsx).
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


# ── Controlled value types ───────────────────────────────

ItemType = Literal["System", "Product", "Component", "Material"]

FunctionalUnit = Literal[
    "Square meter [m^2]",
    "Meter cube [m^3]",
    "Linear meter [lm]",
    "Piece",
    "Liter",
]

SaleType = Literal["Direct sale", "Retailers"]

SafetyAnswer = Literal["Yes", "No", "n.a."]

UvResistance = Literal["Cat. 0", "Cat. 1", "Cat. 2", "Cat. 3", "Cat. 4"]

PerformanceCategoryLiteral = Literal[
    "Mechanical", "Thermal", "Acoustic", "Fire", "Durability", "Environmental", "Other",
]

FireResistance = Literal[
    "A1",
    "A2-s1,d0", "A2-s1,d1", "A2-s1,d2",
    "A2-s2,d0", "A2-s2,d1", "A2-s2,d2",
    "A2-s3,d0", "A2-s3,d1", "A2-s3,d2",
    "B-s1,d0", "B-s1,d1", "B-s1,d2",
    "B-s2,d0", "B-s2,d1", "B-s2,d2",
    "B-s3,d0", "B-s3,d1", "B-s3,d2",
    "C-s1,d0", "C-s1,d1", "C-s1,d2",
    "C-s2,d0", "C-s2,d1", "C-s2,d2",
    "C-s3,d0", "C-s3,d1", "C-s3,d2",
    "D-s1,d0", "D-s1,d1", "D-s1,d2",
    "D-s2,d0", "D-s2,d1", "D-s2,d2",
    "D-s3,d0", "D-s3,d1", "D-s3,d2",
    "E", "F",
]

TransportMethod = Literal[
    "track >32 ton",
    "16< track < 32 ton",
    "7.5< track < 16 ton",
    "3.5< track < 7.5 ton",
    "track < 3.5 ton",
]

EuVehicleClass = Literal["EURO 3", "EURO 4", "EURO 5", "EURO 6"]


# ── Overview ──────────────────────────────────────────────

class SimpleProductInfo(BaseModel):
    product_name: Optional[str] = Field(
        None,
        description="The COMMERCIAL / MARKETING name of the product line. "
                    "Prefer the brand-style product line name (e.g. 'Porotherm BIO', "
                    "'VERSATILE', 'Climaplus 4S', 'Ytong Smart') over a generic category "
                    "label ('Blocchi in laterizio', 'Serramenti esterni', 'Insulation "
                    "panel') or a raw technical code ('Pth BIO inc 35-25/19 P 50', "
                    "'18313570'). When both appear, pick the commercial line name and put "
                    "the technical code into the 'uid' field. If the document only shows a "
                    "technical code with no commercial name, use the technical code here.",
    )
    product_description: Optional[str] = None
    uid: Optional[str] = None
    item_type: Optional[ItemType] = None
    product_family: Optional[str] = None  # kept as free text — overridden from Pass 1
    product_family_code: Optional[str] = None  # auto-mapped in extract.py
    intended_use: Optional[str] = None
    serial_number: Optional[str] = None
    batch_number: Optional[str] = None
    gtin: Optional[str] = None
    functional_unit: Optional[FunctionalUnit] = None
    standard_dimension: Optional[str] = Field(
        None,
        description="Product dimensions as Width × Height (× Depth) with units. "
                    "Examples: '1230 × 1480 mm', '1.23 × 1.48 m', '600 × 250 × 100 mm'. "
                    "Look in technical sheets, DoP and order/commessa data — keywords: "
                    "'Dimensioni', 'Dimensions', 'WxH', 'Larghezza × Altezza', 'Misure', "
                    "'Standard sizes', 'Sizes available'. "
                    "For MADE-TO-MEASURE products (e.g. windows, doors), there is often no "
                    "single standard size — in that case use the REPRESENTATIVE dimension "
                    "given on the test/DoP sample or order (e.g. the tested window size "
                    "'1230 × 1480 mm'). Only return null if no dimension appears anywhere.",
    )
    weight: Optional[str] = Field(
        None,
        description="Weight of ONE physical product unit (one window, one brick, one panel) "
                    "with units. Examples: '38 kg' (one window), '13 kg' (one brick), "
                    "'12.5 kg/m²' (panel). "
                    "Keywords for the right value: 'Peso del prodotto', 'Product weight', "
                    "'Mass of one unit', 'Massa di un pezzo'. "
                    "DO NOT confuse with: 'reference flow', 'flusso di riferimento', "
                    "'declared unit = 1000 kg' (those are the EPD's LCA reference quantity, "
                    "NOT the product's weight) — return null if you only find a reference "
                    "flow, never the reference flow itself. Also do NOT use 'peso "
                    "specifico' (specific weight / density, kg/m³) for this field — that "
                    "belongs in the performance section.",
    )
    production_period: Optional[str] = Field(
        None,
        description="Production validity period as a DATE RANGE in format "
                    "'YYYY-MM-DD to YYYY-MM-DD' (preferred) or 'YYYY-MM to YYYY-MM' or "
                    "'YYYY to YYYY'. Examples: '2024-01-01 to 2024-12-31', '2022-06 to 2027-06', "
                    "'2020 to 2025'. Look for: a 'valid from / valid until' range on a "
                    "Certificate; an 'EPD validity' range on an EPD; a 'period of "
                    "manufacture' on a DoP. If only a single date is found (e.g., issue date), "
                    "return that single date in YYYY-MM-DD form; do NOT invent a range. "
                    "Keywords: 'Production', 'Periodo di produzione', 'Validità', "
                    "'Valid from', 'Valid until', 'Data di emissione', 'Data di scadenza'.",
    )


class SimpleManufacturer(BaseModel):
    company_name: Optional[str] = Field(
        None, description="Manufacturer legal/trade name (e.g., 'Eurofinestra s.a.s'). NOT an address.",
    )
    company_description: Optional[str] = Field(
        None,
        description="A concise 1-3 sentence description of the MANUFACTURER (who they "
                    "are, what they produce, sector/specialisation). SYNTHESIZE this from "
                    "any available context — the fetched website, brochures, document "
                    "headers/footers, or the product range. Always provide a short "
                    "description when the manufacturer is identified; only return null if "
                    "you truly have no information about the company.",
    )
    address: Optional[str] = Field(
        None,
        description="Full registered/legal address of the manufacturer including "
                    "street, number, postal code, city, province, country (e.g., "
                    "'Via dell'Industria 2, 46037 Governolo (MN), Italy'). NOT just a city name.",
    )
    website: Optional[str] = None
    manufacturing_site: Optional[str] = Field(
        None,
        description="Full physical address of the production plant — street, number, "
                    "postal code, city, province, country. NEVER just the company name. "
                    "If the document says e.g. 'Stabilimento Eurofinestra, SP482 95, "
                    "Governolo (MN)', extract 'SP482 95, Governolo (MN)'. "
                    "If the plant address is not explicitly stated, return null "
                    "(don't substitute the legal address or the company name).",
    )
    email: Optional[str] = None
    phone: Optional[str] = None
    sale_type: Optional[SaleType] = Field(
        None,
        description="How the product is sold. Infer from context: choose 'Direct sale' "
                    "when the document/website indicates the manufacturer sells its own "
                    "products directly (own brand, 'vendita diretta', factory/showroom, "
                    "made-to-order by the maker); choose 'Retailers' when sold through "
                    "third-party dealers/distributors. For a manufacturer publishing its "
                    "own product passport, 'Direct sale' is the usual choice.",
    )


class SimpleOverview(BaseModel):
    product_info: SimpleProductInfo = Field(default_factory=SimpleProductInfo)
    manufacturer: SimpleManufacturer = Field(default_factory=SimpleManufacturer)


# ── Performance ───────────────────────────────────────────

class SimplePerformanceValue(BaseModel):
    property_name: str
    # Constrained: forces Gemini to pick the right bucket so the frontend
    # can group values under the correct accordion (Mechanical, Thermal, etc.)
    category: PerformanceCategoryLiteral = "Other"
    value: Optional[str] = None
    unit: Optional[str] = None
    test_standard: Optional[str] = None


class SimplePerformance(BaseModel):
    values: list[SimplePerformanceValue] = Field(default_factory=list)
    # Controlled performance fields with predefined values
    fire_resistance: Optional[FireResistance] = None
    uv_resistance: Optional[UvResistance] = None


# ── Compliance ────────────────────────────────────────────

class SimpleSafety(BaseModel):
    contains_cmrs: Optional[SafetyAnswer] = None
    contains_svhcs: Optional[SafetyAnswer] = None
    contains_pentane: Optional[SafetyAnswer] = None
    contains_pfas: Optional[SafetyAnswer] = None
    has_flame_retardancy: Optional[SafetyAnswer] = None
    complies_rohs: Optional[SafetyAnswer] = None
    produces_voc: Optional[SafetyAnswer] = None
    contains_heavy_metals: Optional[SafetyAnswer] = None
    contains_asbestos: Optional[SafetyAnswer] = None
    complies_child_labor: Optional[SafetyAnswer] = None
    other_declaration: Optional[str] = None  # free text


class SimpleCertification(BaseModel):
    name: Optional[str] = None
    reference_number: Optional[str] = None
    issuing_body: Optional[str] = None
    valid_until: Optional[str] = None
    scope: Optional[str] = None


class SimpleCompliance(BaseModel):
    dop_reference: Optional[str] = None
    dop_standard: Optional[str] = None
    doc_reference: Optional[str] = None
    ce_marking: Optional[str] = None
    quality_control: Optional[str] = None
    safety: SimpleSafety = Field(default_factory=SimpleSafety)
    product_certifications: list[SimpleCertification] = Field(default_factory=list)
    company_certifications: list[SimpleCertification] = Field(default_factory=list)
    other_labels: Optional[str] = None


# ── Composition ───────────────────────────────────────────

class SimpleSupplier(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    transport_method: Optional[TransportMethod] = None
    eu_vehicle_class: Optional[EuVehicleClass] = None
    distance_km: Optional[float] = None


class SimpleMaterial(BaseModel):
    material_id: Optional[str] = Field(
        None,
        description="Internal material code/identifier from the BoM (e.g. 'WB_CLA_01'). "
                    "If the user-provided BoM has an 'id=' column, copy it here verbatim.",
    )
    description: Optional[str] = Field(
        None,
        description="Material name or description (e.g. 'Clay', 'Petcoke', 'Recycled aluminum'). "
                    "Match the BoM description if a BoM was provided.",
    )
    unit: Optional[str] = Field(
        None,
        description="Unit of measure for the quantity (e.g. 'kg', '%', 'g', 'pieces'). "
                    "REQUIRED whenever quantity is set. If the BoM says 'qty=639.6 kg', "
                    "set unit='kg'.",
    )
    quantity: Optional[str] = Field(
        None,
        description="Numeric quantity of this material per functional unit, as a STRING. "
                    "Examples: '639.6', '78', '46', '0.5'. "
                    "COPY directly from BoM 'qty=...' rows (e.g. 'qty=639.6 kg' → "
                    "quantity='639.6', unit='kg'). If the BoM provides a numeric quantity, "
                    "you MUST fill this field — do NOT leave it null. The same applies to "
                    "explicit EPD composition tables. Do NOT include the unit here (use "
                    "the 'unit' field for that).",
    )
    percentage: Optional[str] = Field(
        None,
        description="Mass percentage in the product as a STRING (0-100, e.g. '12.5', '88'). "
                    "Only set when explicitly stated as %; do NOT compute from kg values.",
    )
    origin: Optional[str] = None
    recyclable: Optional[str] = None
    recycled_content: Optional[str] = Field(
        None,
        description="Recycled fraction of this material as a STRING (e.g. '10', '> 15', "
                    "'10-20'). Only set when the BoM or EPD explicitly states the recycled "
                    "content for this specific material row.",
    )
    suppliers: list[SimpleSupplier] = Field(default_factory=list)


class SimpleComposition(BaseModel):
    materials: list[SimpleMaterial] = Field(default_factory=list)


# ── Lifecycle ─────────────────────────────────────────────

class SimpleLifecycleStage(BaseModel):
    stage_code: str
    gwp_total: Optional[float] = None
    gwp_fossil: Optional[float] = None
    gwp_biogenic: Optional[float] = None
    odp: Optional[float] = None
    ap: Optional[float] = None
    ep_freshwater: Optional[float] = None
    ep_marine: Optional[float] = None
    pocp: Optional[float] = None
    adp_minerals: Optional[float] = None
    adp_fossil: Optional[float] = None
    wdp: Optional[float] = None


class SimpleLifecycle(BaseModel):
    reference_year: Optional[str] = None
    process_description: Optional[str] = None
    stages: list[SimpleLifecycleStage] = Field(default_factory=list)


# ── Top-level ─────────────────────────────────────────────

class SimpleExtractionOutput(BaseModel):
    """Simplified extraction output for Gemini structured output."""
    overview: SimpleOverview = Field(default_factory=SimpleOverview)
    performance: SimplePerformance = Field(default_factory=SimplePerformance)
    compliance: SimpleCompliance = Field(default_factory=SimpleCompliance)
    composition: SimpleComposition = Field(default_factory=SimpleComposition)
    lifecycle: SimpleLifecycle = Field(default_factory=SimpleLifecycle)
