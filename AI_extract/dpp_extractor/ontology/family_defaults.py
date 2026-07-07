"""
Smart defaults per product family from DeePPy_data_ontology.xlsx.

When a field is not found in the document, these defaults are applied
with confidence=MEDIUM and a note asking the user to confirm.
"""

from .enums import ProductFamily


# ProductFamily → default functional unit
FUNCTIONAL_UNIT_DEFAULTS: dict[ProductFamily, str] = {
    # Windows, doors, shutters → per square meter (EU EPD convention for DWS).
    # CPR/EN 14351 requires performance per m² of installed glazed area.
    ProductFamily.DWS: "Square meter [m^2]",
    ProductFamily.SAP: "Piece",  # Sanitary appliances
    ProductFamily.SHA: "Piece",  # Space heating
    ProductFamily.FFF: "Piece",  # Fire fighting equipment
    ProductFamily.LAD: "Piece",  # Ladders

    # Insulation, membranes, finishes → per m²
    ProductFamily.TIP: "Square meter [m^2]",
    ProductFamily.MEM: "Square meter [m^2]",
    ProductFamily.WCF: "Square meter [m^2]",  # Wall/ceiling finishes
    ProductFamily.FLO: "Square meter [m^2]",  # Floorings
    ProductFamily.ROC: "Square meter [m^2]",  # Roof coverings
    ProductFamily.GYP: "Square meter [m^2]",  # Gypsum
    ProductFamily.GEO: "Square meter [m^2]",  # Geotextiles
    ProductFamily.CWP: "Square meter [m^2]",  # Curtain walling

    # Concrete, masonry, aggregates → per m³ or piece
    ProductFamily.PCP: "Piece",    # Precast concrete
    ProductFamily.MAS: "Piece",    # Masonry units
    ProductFamily.AGG: "Meter cube [m^3]",  # Aggregates
    ProductFamily.CMG: "Meter cube [m^3]",  # Concrete/mortar/grout

    # Cement, limes → per kg (no exact match in Literal, use Piece)
    ProductFamily.CEM: "Meter cube [m^3]",

    # Cables, pipes → per linear meter
    ProductFamily.CAB: "Linear meter [lm]",
    ProductFamily.PTA: "Linear meter [lm]",  # Pipes
    ProductFamily.DWP: "Linear meter [lm]",  # Drinking water pipes
    ProductFamily.WWD: "Linear meter [lm]",  # Wastewater

    # Steel, timber structural → per linear meter or piece
    ProductFamily.SMP: "Linear meter [lm]",  # Structural metallic
    ProductFamily.STP: "Linear meter [lm]",  # Structural timber
    ProductFamily.RPS: "Linear meter [lm]",  # Reinforcing steel

    # Small products → Piece
    ProductFamily.FIX: "Piece",  # Fixings
    ProductFamily.SBE: "Piece",  # Structural bearings
    ProductFamily.SEA: "Liter",  # Sealants
    ProductFamily.ADH: "Liter",  # Adhesives

    # Building kits/systems
    ProductFamily.KAS: "Piece",
    ProductFamily.FPP: "Square meter [m^2]",  # Fire protection
    ProductFamily.WBP: "Square meter [m^2]",  # Wood panels
    ProductFamily.CHI: "Piece",  # Chimneys
    ProductFamily.CIF: "Piece",  # Road equipment
    ProductFamily.RCP: "Meter cube [m^3]",  # Road construction
    ProductFamily.GLA: "Square meter [m^2]",  # Glass
}

# ProductFamily → default item type
ITEM_TYPE_DEFAULTS: dict[ProductFamily, str] = {
    # Systems (multi-component assemblies)
    ProductFamily.DWS: "System",
    ProductFamily.CWP: "System",
    ProductFamily.KAS: "System",
    ProductFamily.FFF: "System",
    ProductFamily.SHA: "System",
    ProductFamily.CHI: "System",

    # Materials (raw/bulk)
    ProductFamily.CEM: "Material",
    ProductFamily.AGG: "Material",
    ProductFamily.ADH: "Material",
    ProductFamily.SEA: "Material",
    ProductFamily.CMG: "Material",
    ProductFamily.GEO: "Material",

    # Components (individual parts)
    ProductFamily.FIX: "Component",
    ProductFamily.SBE: "Component",
    ProductFamily.RPS: "Component",
    ProductFamily.CAB: "Component",

    # Default for everything else is "Product"
}


def get_default_functional_unit(family: ProductFamily) -> str | None:
    """Get default functional unit for a product family, or None."""
    return FUNCTIONAL_UNIT_DEFAULTS.get(family)


def get_default_item_type(family: ProductFamily) -> str:
    """Get default item type for a product family."""
    return ITEM_TYPE_DEFAULTS.get(family, "Product")
