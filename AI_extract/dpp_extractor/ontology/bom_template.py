"""
Product-family-specific Bill of Materials templates from
DeePPy_data_ontology.xlsx — Bill_of_materials sheet.

These template entries are used to:
  - Suggest expected material categories to the AI extractor
  - Pre-populate the BOM in the frontend when no extraction is available
  - Validate that key materials for a family are accounted for
"""

from .enums import ProductFamily


# ---------------------------------------------------------------------------
# DWS — Doors, Windows, Shutters (17 materials per ontology BOM)
# ---------------------------------------------------------------------------

DWS_BOM_TEMPLATE: list[str] = [
    "Wooden frame",
    "Cork frame",
    "Laminated glass panel (in), low-E, 33.1",
    "Laminated glass panel (out), low-E, 33.1",
    "Space bar",
    "PVB",
    "Adhesives",
    "Handle",
    "Hardware",
    "Wooden drip / threshold",
    "Gasket, sealing",
    "Primer coat (impregnante)",
    "Base coat (fondo)",
    "Top coat (finitura)",
    "Thermal-insulated sub-frame (monoblocco)",
    "Installation cover",
    "Solar shading system",
]


# ---------------------------------------------------------------------------
# Registry: ProductFamily → BOM template
# ---------------------------------------------------------------------------

BOM_TEMPLATES: dict[ProductFamily, list[str]] = {
    ProductFamily.DWS: DWS_BOM_TEMPLATE,
    # Add other families as the ontology expands.
}


def get_bom_template(family: ProductFamily) -> list[str]:
    """Get the BOM template for a product family. Empty list when not defined."""
    return BOM_TEMPLATES.get(family, [])
