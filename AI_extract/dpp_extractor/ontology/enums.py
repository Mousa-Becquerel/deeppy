"""
Enumeration types derived from DeePPy_data_ontology.xlsx — Pre-selected_value sheet.

These enums are the single source of truth for all dropdown/select fields
in the DPP extraction pipeline and frontend.
"""

from enum import Enum


class ItemType(str, Enum):
    """Type of item in the product passport."""
    SYSTEM = "System"
    PRODUCT = "Product"
    COMPONENT = "Component"
    MATERIAL = "Material"


class ProductFamily(str, Enum):
    """
    CPR product families from EU Construction Products Regulation.
    Code is the short identifier, value is the full name.
    """
    PCP = "Precast normal/lightweight/autoclaved aerated concrete products"
    DWS = "Doors, windows, shutters, gates and related building hardware"
    MEM = "Membranes, including liquid applied and kits"
    TIP = "Thermal insulation products - Composite insulating kits/systems"
    SBE = "Structural bearings - Pins for structural joints"
    CHI = "Chimneys, flues and specific products"
    GYP = "Gypsum products"
    GEO = "Geotextiles, geomembranes, and related products"
    CWP = "Curtain walling/cladding/structural sealant glazing"
    FFF = "Fixed fire fighting equipment"
    SAP = "Sanitary appliances"
    CIF = "Circulation fixtures: road equipment"
    STP = "Structural timber products/elements and ancillaries"
    WBP = "Wood based panels and elements"
    CEM = "Cement, building limes and other hydraulic binders"
    RPS = "Reinforcing and prestressing steel for concrete - Post-tensioning kits"
    MAS = "Masonry and related products - Masonry units, mortars, and ancillaries"
    WWD = "Wastewater engineering products"
    FLO = "Floorings"
    SMP = "Structural metallic products and ancillaries"
    WCF = "Internal & external wall and ceiling finishes. Internal partition kits"
    ROC = "Roof coverings, roof lights, roof windows, and ancillary products. Roof kits"
    RCP = "Road construction products"
    AGG = "Aggregates"
    ADH = "Construction adhesives"
    CMG = "Products related to concrete, mortar and grout"
    SHA = "Space heating appliances"
    PTA = "Pipes-tanks and ancillaries not in contact with water for human consumption"
    DWP = "Construction products in contact with water intended for human consumption"
    GLA = "Flat glass, profiled glass and glass block products"
    CAB = "Power, control and communication cables"
    SEA = "Sealants for joints"
    FIX = "Fixings"
    KAS = "Building kits, units, and prefabricated elements"
    FPP = "Fire stopping, sealing and protective products - Fire retardant products"
    LAD = "Attached ladders"
    OTH = "Other construction products"


# Reverse lookup: family code → full name
PRODUCT_FAMILY_NAMES: dict[str, str] = {f.name: f.value for f in ProductFamily}

# Reverse lookup: full name → family code
PRODUCT_FAMILY_CODES: dict[str, str] = {f.value: f.name for f in ProductFamily}


class FunctionalUnit(str, Enum):
    """Functional/declared unit for the product."""
    SQUARE_METER = "Square meter [m^2]"
    CUBIC_METER = "Meter cube [m^3]"
    LINEAR_METER = "Linear meter [lm]"
    PIECE = "Piece"
    LITER = "Liter"


class DimensionUnit(str, Enum):
    """Unit for standard dimensions."""
    MM = "mm"
    CM = "cm"
    M = "m"
    L = "l"


class SaleType(str, Enum):
    """How the product is sold."""
    DIRECT = "Direct sale"
    RETAILERS = "Retailers"


class FireResistanceClass(str, Enum):
    """EU fire resistance classification (EN 13501-1)."""
    A1 = "A1"
    A2_S1_D0 = "A2-s1,d0"
    A2_S1_D1 = "A2-s1,d1"
    A2_S1_D2 = "A2-s1,d2"
    A2_S2_D0 = "A2-s2,d0"
    A2_S2_D1 = "A2-s2,d1"
    A2_S2_D2 = "A2-s2,d2"
    A2_S3_D0 = "A2-s3,d0"
    A2_S3_D1 = "A2-s3,d1"
    A2_S3_D2 = "A2-s3,d2"
    B_S1_D0 = "B-s1,d0"
    B_S1_D1 = "B-s1,d1"
    B_S1_D2 = "B-s1,d2"
    B_S2_D0 = "B-s2,d0"
    B_S2_D1 = "B-s2,d1"
    B_S2_D2 = "B-s2,d2"
    B_S3_D0 = "B-s3,d0"
    B_S3_D1 = "B-s3,d1"
    B_S3_D2 = "B-s3,d2"
    C_S1_D0 = "C-s1,d0"
    C_S1_D1 = "C-s1,d1"
    C_S1_D2 = "C-s1,d2"
    C_S2_D0 = "C-s2,d0"
    C_S2_D1 = "C-s2,d1"
    C_S2_D2 = "C-s2,d2"
    C_S3_D0 = "C-s3,d0"
    C_S3_D1 = "C-s3,d1"
    C_S3_D2 = "C-s3,d2"
    D_S1_D0 = "D-s1,d0"
    D_S1_D1 = "D-s1,d1"
    D_S1_D2 = "D-s1,d2"
    D_S2_D0 = "D-s2,d0"
    D_S2_D1 = "D-s2,d1"
    D_S2_D2 = "D-s2,d2"
    D_S3_D0 = "D-s3,d0"
    D_S3_D1 = "D-s3,d1"
    D_S3_D2 = "D-s3,d2"
    E = "E"
    F = "F"


class UVResistanceCategory(str, Enum):
    """UV resistance category."""
    CAT_0 = "Cat. 0"
    CAT_1 = "Cat. 1"
    CAT_2 = "Cat. 2"
    CAT_3 = "Cat. 3"
    CAT_4 = "Cat. 4"


class SafetyAnswer(str, Enum):
    """Yes/No/N.A. for safety compliance questions."""
    YES = "Yes"
    NO = "No"
    NA = "n.a."


class TransportMethod(str, Enum):
    """Means of transportation for supply chain."""
    TRUCK_OVER_32T = "track >32 ton"
    TRUCK_16_32T = "16< track < 32 ton"
    TRUCK_7_5_16T = "7.5< track < 16 ton"
    TRUCK_3_5_7_5T = "3.5< track < 7.5 ton"
    TRUCK_UNDER_3_5T = "track < 3.5 ton"


class EUVehicleClass(str, Enum):
    """EU emission vehicle class for transport."""
    EURO_3 = "EURO 3"
    EURO_4 = "EURO 4"
    EURO_5 = "EURO 5"
    EURO_6 = "EURO 6"


class DocumentType(str, Enum):
    """Types of construction product documents the system can process."""
    DOP = "DoP"                     # Declaration of Performance
    TECHNICAL_SHEET = "TechnicalSheet"  # Scheda Tecnica
    EPD = "EPD"                     # Environmental Product Declaration
    SDS = "SDS"                     # Safety Data Sheet
    CERTIFICATE = "Certificate"     # ISO, CE, FPC, thermal, acoustic certs
    CATALOG = "Catalog"             # Product catalog / brochure
    BOM = "BOM"                     # Bill of Materials (Distinta Base)
    DRAWING = "Drawing"             # 2D/3D technical drawings
    METHOD_STATEMENT = "MethodStatement"  # Installation/maintenance guides
    OTHER = "Other"


class ConfidenceLevel(str, Enum):
    """
    Confidence level for extracted field values.
    Maps directly to the frontend Conf component.
    """
    HIGH = "high"       # Clearly extracted, single authoritative source → green "Auto"
    MEDIUM = "medium"   # Extracted but ambiguous/needs review → amber "Review"
    LOW = "low"         # Not found or very uncertain → red "Missing"


class DPPSection(str, Enum):
    """Top-level sections of the Digital Product Passport."""
    OVERVIEW = "Overview"
    COMPOSITION = "Composition"
    PERFORMANCE = "Performance"
    COMPLIANCE = "Compliance"
    LIFECYCLE = "Lifecycle"
    DOCUMENTS = "Documents"


class PerformanceCategory(str, Enum):
    """Categories within the Performance section."""
    MECHANICAL = "Mechanical"
    THERMAL = "Thermal"
    ACOUSTIC = "Acoustic"
    FIRE = "Fire"
    DURABILITY = "Durability"
    ENVIRONMENTAL = "Environmental"
    OTHER = "Other"
