"""
Field definitions derived from DeePPy_data_ontology.xlsx — Data_ontology sheet.

Each FieldDefinition represents one extractable field in the DPP passport.
This registry is the single source of truth for what fields exist, their
hierarchy, and their constraints.
"""

from dataclasses import dataclass
from typing import Optional

from .enums import DPPSection


@dataclass(frozen=True)
class FieldDefinition:
    """Metadata for a single ontology field."""
    field_id: str               # Unique identifier (snake_case)
    section: DPPSection         # Which DPP section this belongs to
    tier1: str                  # Top-level grouping
    tier2: str                  # Sub-grouping
    tier3: str                  # Field name as in ontology
    unit: Optional[str]         # Expected unit (None if text)
    required: bool              # Required or Optional in ontology
    format: str                 # Expected format (Text, Number, PDF, etc.)
    has_preselected: bool       # Whether Pre-selected_value applies
    max_length: Optional[str]   # DB column type hint
    notes: Optional[str] = None # Additional notes from ontology


# ---------------------------------------------------------------------------
# OVERVIEW — General Product Information
# ---------------------------------------------------------------------------

OVERVIEW_PRODUCT_INFO_FIELDS: list[FieldDefinition] = [
    FieldDefinition(
        field_id="product_name",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Product information", tier3="Product Name",
        unit=None, required=True, format="Text",
        has_preselected=False, max_length="VARCHAR(255)",
    ),
    FieldDefinition(
        field_id="product_image",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Product information", tier3="Product image",
        unit=None, required=False, format="JPEG, PNG, etc.",
        has_preselected=False, max_length=None,
    ),
    FieldDefinition(
        field_id="product_description",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Product information", tier3="Product description",
        unit=None, required=False, format="Text",
        has_preselected=False, max_length="VARCHAR(255)",
    ),
    FieldDefinition(
        field_id="uid",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Product information", tier3="Unique Product Identifier (UID)",
        unit=None, required=True, format="Alphanumeric",
        has_preselected=False, max_length="VARCHAR(255)",
    ),
    FieldDefinition(
        field_id="item_type",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Product information", tier3="Item type",
        unit=None, required=True, format="Text",
        has_preselected=True, max_length="VARCHAR(255)",
    ),
    FieldDefinition(
        field_id="product_family",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Product information", tier3="Product family",
        unit=None, required=True, format="Text",
        has_preselected=True, max_length="VARCHAR(255)",
    ),
    FieldDefinition(
        field_id="intended_use",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Product information", tier3="Intended use",
        unit=None, required=True, format="Text",
        has_preselected=False, max_length="VARCHAR(255)",
    ),
]

OVERVIEW_OPTIONAL_FIELDS: list[FieldDefinition] = [
    FieldDefinition(
        field_id="serial_number",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Optional information", tier3="Serial Number (SN)",
        unit=None, required=False, format="Alphanumeric",
        has_preselected=False, max_length="VARCHAR(50)",
    ),
    FieldDefinition(
        field_id="batch_number",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Optional information", tier3="Batch Number (BN)",
        unit=None, required=False, format="Alphanumeric",
        has_preselected=False, max_length="VARCHAR(50)",
    ),
    FieldDefinition(
        field_id="gtin",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Optional information", tier3="Global Trade Identification Number (GTIN)",
        unit=None, required=False, format="Alphanumeric",
        has_preselected=False, max_length="VARCHAR(50)",
    ),
    FieldDefinition(
        field_id="functional_unit",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Optional information", tier3="Functional unit",
        unit="m^2, piece, etc.", required=True, format="Text",
        has_preselected=True, max_length="VARCHAR(20)",
    ),
    FieldDefinition(
        field_id="standard_dimension",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Optional information", tier3="Standard dimension (WxDxH)",
        unit="mm or multiple", required=False, format="Number",
        has_preselected=True, max_length="VARCHAR(100)",
    ),
    FieldDefinition(
        field_id="weight",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Optional information", tier3="Weight",
        unit="kg", required=False, format="Number",
        has_preselected=False, max_length="DECIMAL(10,3)",
    ),
    FieldDefinition(
        field_id="production_period",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Optional information", tier3="Production period",
        unit=None, required=True, format="Date range",
        has_preselected=False, max_length="DATERANGE",
    ),
]

OVERVIEW_MANUFACTURER_FIELDS: list[FieldDefinition] = [
    FieldDefinition(
        field_id="company_name",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Manufacturer", tier3="Company name",
        unit=None, required=True, format="Text",
        has_preselected=False, max_length="VARCHAR(255)",
    ),
    FieldDefinition(
        field_id="company_description",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Manufacturer", tier3="Company description",
        unit=None, required=False, format="Text",
        has_preselected=False, max_length="VARCHAR(255)",
    ),
    FieldDefinition(
        field_id="address",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Manufacturer", tier3="Address",
        unit=None, required=True, format="Text",
        has_preselected=False, max_length="VARCHAR(255)",
    ),
    FieldDefinition(
        field_id="website",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Manufacturer", tier3="Website",
        unit=None, required=True, format="Text",
        has_preselected=False, max_length="VARCHAR(255)",
    ),
    FieldDefinition(
        field_id="manufacturing_site",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Manufacturer", tier3="Manufacturing site",
        unit=None, required=True, format="Map",
        has_preselected=False, max_length="VARCHAR(255)",
    ),
    FieldDefinition(
        field_id="email",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Manufacturer", tier3="Mail",
        unit=None, required=True, format="Mail",
        has_preselected=False, max_length="VARCHAR(50)",
    ),
    FieldDefinition(
        field_id="phone",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Manufacturer", tier3="Phone",
        unit=None, required=False, format="Number",
        has_preselected=False, max_length="VARCHAR(50)",
    ),
    FieldDefinition(
        field_id="sale_type",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Manufacturer", tier3="Sale type",
        unit=None, required=False, format="Text",
        has_preselected=True, max_length="VARCHAR(255)",
    ),
]

OVERVIEW_VERSION_FIELDS: list[FieldDefinition] = [
    FieldDefinition(
        field_id="version_history",
        section=DPPSection.OVERVIEW, tier1="General Product Information",
        tier2="Version hystory", tier3="Versions",
        unit=None, required=False, format="Alphanumeric",
        has_preselected=False, max_length="VARCHAR(255)",
    ),
]

# ---------------------------------------------------------------------------
# COMPLIANCE — Declarations, Safety, Certifications
# ---------------------------------------------------------------------------

COMPLIANCE_DECLARATION_FIELDS: list[FieldDefinition] = [
    FieldDefinition(
        field_id="dop",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Declaration of Performance", tier3="DoP",
        unit=None, required=False, format="PDF",
        has_preselected=False, max_length=None,
    ),
    FieldDefinition(
        field_id="doc",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Declaration of Conformity", tier3="DoC",
        unit=None, required=False, format="PDF",
        has_preselected=False, max_length=None,
    ),
    FieldDefinition(
        field_id="ce_marking",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="CE marking", tier3="CE",
        unit=None, required=False, format="PDF",
        has_preselected=False, max_length=None,
    ),
    FieldDefinition(
        field_id="quality_control",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Quality control", tier3="Quality",
        unit=None, required=False, format="PDF",
        has_preselected=False, max_length=None,
    ),
]

COMPLIANCE_SAFETY_FIELDS: list[FieldDefinition] = [
    FieldDefinition(
        field_id="contains_cmrs",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Safety information", tier3="Does it contain any CMRs candidates?",
        unit=None, required=False, format="Text",
        has_preselected=True, max_length="BOOLEAN",
    ),
    FieldDefinition(
        field_id="contains_svhcs",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Safety information", tier3="Does it contain any SVHCs candidates?",
        unit=None, required=False, format="Text",
        has_preselected=True, max_length="BOOLEAN",
    ),
    FieldDefinition(
        field_id="contains_pentane",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Safety information", tier3="Does it contain pentane?",
        unit=None, required=False, format="Text",
        has_preselected=True, max_length="BOOLEAN",
    ),
    FieldDefinition(
        field_id="contains_pfas",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Safety information", tier3="Does it contain PFAS?",
        unit=None, required=False, format="Text",
        has_preselected=True, max_length="BOOLEAN",
    ),
    FieldDefinition(
        field_id="has_flame_retardancy",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Safety information", tier3="Does it have flame retardancy?",
        unit=None, required=False, format="Text",
        has_preselected=True, max_length="BOOLEAN",
    ),
    FieldDefinition(
        field_id="complies_rohs",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Safety information", tier3="Does it comply with RoHS?",
        unit=None, required=False, format="Text",
        has_preselected=True, max_length="BOOLEAN",
    ),
    FieldDefinition(
        field_id="produces_voc",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Safety information", tier3="Does it produces VOC emission?",
        unit=None, required=False, format="Text",
        has_preselected=True, max_length="BOOLEAN",
    ),
    FieldDefinition(
        field_id="contains_heavy_metals",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Safety information", tier3="Does it cointain heavy metals or halogenated?",
        unit=None, required=False, format="Text",
        has_preselected=True, max_length="BOOLEAN",
    ),
    FieldDefinition(
        field_id="contains_asbestos",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Safety information", tier3="Does it cointain asbestos?",
        unit=None, required=False, format="Text",
        has_preselected=True, max_length="BOOLEAN",
    ),
    FieldDefinition(
        field_id="complies_child_labor",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Safety information", tier3="Does it comply with Child labor regulation? Y/N",
        unit=None, required=False, format="Text",
        has_preselected=True, max_length="BOOLEAN",
    ),
    FieldDefinition(
        field_id="other_safety_declaration",
        section=DPPSection.COMPLIANCE, tier1="Declaration of Performance & Conformity",
        tier2="Safety information", tier3="Other declaration",
        unit=None, required=False, format="PDF",
        has_preselected=False, max_length=None,
    ),
]

COMPLIANCE_LABELING_FIELDS: list[FieldDefinition] = [
    FieldDefinition(
        field_id="product_certifications",
        section=DPPSection.COMPLIANCE, tier1="Labeling",
        tier2="Product certifications", tier3="Product certification #1..#n",
        unit=None, required=False, format="PDF or link",
        has_preselected=False, max_length=None,
        notes="E.g.: EPD, ECOLABEL, DECLARE, recycled content, carbon footprint, VOC emission",
    ),
    FieldDefinition(
        field_id="company_certifications",
        section=DPPSection.COMPLIANCE, tier1="Labeling",
        tier2="Company and supply chain certification", tier3="Company certification #1..#n",
        unit=None, required=False, format="PDF or link",
        has_preselected=False, max_length=None,
        notes="E.g.: ISO 9001, ISO 14001, ISO 50001, EMAS, ISO 20400, EcoVadis, Bcorp",
    ),
    FieldDefinition(
        field_id="other_labels",
        section=DPPSection.COMPLIANCE, tier1="Labeling",
        tier2="Other labels", tier3="Other labels",
        unit=None, required=False, format="PDF or link",
        has_preselected=False, max_length=None,
    ),
]

# ---------------------------------------------------------------------------
# LIFECYCLE — A1 through C4
# ---------------------------------------------------------------------------

LIFECYCLE_A3_FIELDS: list[FieldDefinition] = [
    FieldDefinition(
        field_id="a3_reference_year",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="Reference year", tier3="Reference year",
        unit=None, required=False, format="Date",
        has_preselected=False, max_length="YEAR",
    ),
    FieldDefinition(
        field_id="a3_total_production",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="Total product production", tier3="Total product production",
        unit=None, required=False, format="Number",
        has_preselected=False, max_length="DECIMAL(10,2)",
    ),
    FieldDefinition(
        field_id="a3_process_description",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="Process description", tier3="Process description",
        unit=None, required=False, format="Text",
        has_preselected=False, max_length="TEXT",
    ),
    FieldDefinition(
        field_id="a3_process_steps",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="Process steps", tier3="Process steps",
        unit=None, required=False, format="Text",
        has_preselected=True, max_length=None,
        notes="See Manufacturing_Process sheet for family-specific steps",
    ),
    FieldDefinition(
        field_id="a3_energy_electrical",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="Energy consumption (electrical)", tier3="Energy consumption (electrical)",
        unit="kWh/yr", required=False, format="Number",
        has_preselected=False, max_length="DECIMAL(10,2)",
    ),
    FieldDefinition(
        field_id="a3_renewable_rate_electrical",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="Renewable energy rate (electrical)", tier3="Renewable energy rate (electrical)",
        unit="%", required=False, format="Number",
        has_preselected=False, max_length="DECIMAL(3,2)",
    ),
    FieldDefinition(
        field_id="a3_onsite_pv",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="On-site energy production (PV)", tier3="On-site energy production (PV)",
        unit="kWh/yr", required=False, format="Number",
        has_preselected=False, max_length="DECIMAL(10,2)",
    ),
    FieldDefinition(
        field_id="a3_energy_thermal",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="Energy consumption (thermal)", tier3="Energy consumption (thermal)",
        unit="Sm^3", required=False, format="Number",
        has_preselected=False, max_length="DECIMAL(10,2)",
    ),
    FieldDefinition(
        field_id="a3_renewable_rate_thermal",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="Renewable energy rate (thermal)", tier3="Renewable energy rate (thermal)",
        unit="%", required=False, format="Number",
        has_preselected=False, max_length="DECIMAL(3,2)",
    ),
    FieldDefinition(
        field_id="a3_grid_mix",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="Energy grid mix (fossil/renewable)", tier3="Energy grid mix (fossil/renewable)",
        unit="%", required=False, format="Number",
        has_preselected=False, max_length="DECIMAL(3,2)",
    ),
    FieldDefinition(
        field_id="a3_water_use",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="Water use", tier3="Water use",
        unit="m^3", required=False, format="Number",
        has_preselected=False, max_length="DECIMAL(10,2)",
    ),
    FieldDefinition(
        field_id="a3_packaging",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="Packaging", tier3="Packaging",
        unit=None, required=False, format="Text",
        has_preselected=False, max_length="TEXT",
    ),
    FieldDefinition(
        field_id="a3_waste_material",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="Waste production", tier3="Material",
        unit=None, required=False, format="Text",
        has_preselected=False, max_length="TEXT",
    ),
    FieldDefinition(
        field_id="a3_waste_weight",
        section=DPPSection.LIFECYCLE, tier1="A3 Manufacturing",
        tier2="Waste production", tier3="Weight",
        unit="kg", required=False, format="Number",
        has_preselected=False, max_length="DECIMAL(10,2)",
    ),
]

# ---------------------------------------------------------------------------
# DOCUMENTS — Technical Documentation
# ---------------------------------------------------------------------------

DOCUMENTS_FIELDS: list[FieldDefinition] = [
    FieldDefinition(
        field_id="drawing_2d",
        section=DPPSection.DOCUMENTS, tier1="Technical Documentation",
        tier2="Drawings", tier3="2d model",
        unit=None, required=False, format="PDF, dwg",
        has_preselected=False, max_length=None,
    ),
    FieldDefinition(
        field_id="drawing_3d",
        section=DPPSection.DOCUMENTS, tier1="Technical Documentation",
        tier2="Drawings", tier3="3D model",
        unit=None, required=False, format="IFC, obj, etc.",
        has_preselected=False, max_length=None,
    ),
    FieldDefinition(
        field_id="method_statement_installation",
        section=DPPSection.DOCUMENTS, tier1="Technical Documentation",
        tier2="Method Statement & Guidelines", tier3="Method Statement for Installation",
        unit=None, required=False, format="PDF, link or video",
        has_preselected=False, max_length=None,
    ),
    FieldDefinition(
        field_id="method_statement_maintenance",
        section=DPPSection.DOCUMENTS, tier1="Technical Documentation",
        tier2="Method Statement & Guidelines", tier3="Method Statement for Maintenance and Repair",
        unit=None, required=False, format="PDF, link or video",
        has_preselected=False, max_length=None,
    ),
    FieldDefinition(
        field_id="method_statement_replacement",
        section=DPPSection.DOCUMENTS, tier1="Technical Documentation",
        tier2="Method Statement & Guidelines", tier3="Method Statement for Replacement/refurbishment",
        unit=None, required=False, format="PDF, link or video",
        has_preselected=False, max_length=None,
    ),
    FieldDefinition(
        field_id="method_statement_dismantling",
        section=DPPSection.DOCUMENTS, tier1="Technical Documentation",
        tier2="Method Statement & Guidelines", tier3="Method Statement for Dismantling & EoL",
        unit=None, required=False, format="PDF, link or video",
        has_preselected=False, max_length=None,
    ),
    FieldDefinition(
        field_id="technical_data_sheet",
        section=DPPSection.DOCUMENTS, tier1="Technical Documentation",
        tier2="Technical data sheet", tier3="Technical data sheet",
        unit=None, required=False, format="PDF",
        has_preselected=False, max_length=None,
    ),
    FieldDefinition(
        field_id="brochure",
        section=DPPSection.DOCUMENTS, tier1="Technical Documentation",
        tier2="Brochure and commercial presentation", tier3="Brochure and commercial presentation",
        unit=None, required=False, format="PDF",
        has_preselected=False, max_length=None,
    ),
    FieldDefinition(
        field_id="other_documents",
        section=DPPSection.DOCUMENTS, tier1="Technical Documentation",
        tier2="Other documents", tier3="Other documents",
        unit=None, required=False, format="PDF",
        has_preselected=False, max_length=None,
    ),
]


# ---------------------------------------------------------------------------
# Aggregated collections for easy access
# ---------------------------------------------------------------------------

ALL_OVERVIEW_FIELDS = (
    OVERVIEW_PRODUCT_INFO_FIELDS
    + OVERVIEW_OPTIONAL_FIELDS
    + OVERVIEW_MANUFACTURER_FIELDS
    + OVERVIEW_VERSION_FIELDS
)

ALL_COMPLIANCE_FIELDS = (
    COMPLIANCE_DECLARATION_FIELDS
    + COMPLIANCE_SAFETY_FIELDS
    + COMPLIANCE_LABELING_FIELDS
)

ALL_FIELDS = (
    ALL_OVERVIEW_FIELDS
    + ALL_COMPLIANCE_FIELDS
    + LIFECYCLE_A3_FIELDS
    + DOCUMENTS_FIELDS
)

# Lookup by field_id
FIELD_REGISTRY: dict[str, FieldDefinition] = {f.field_id: f for f in ALL_FIELDS}

# Count required fields (for completeness calculation)
REQUIRED_FIELD_COUNT = sum(1 for f in ALL_FIELDS if f.required)
TOTAL_FIELD_COUNT = len(ALL_FIELDS)
