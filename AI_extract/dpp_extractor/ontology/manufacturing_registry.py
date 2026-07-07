"""
Product-family-specific manufacturing process steps from
DeePPy_data_ontology.xlsx — Manufacturing_process sheet.
"""

from .enums import ProductFamily


# ---------------------------------------------------------------------------
# DWS — Doors, Windows, Shutters
# ---------------------------------------------------------------------------

DWS_PROCESS_STEPS: list[str] = [
    "Material procurement",
    "Inbound logistic",
    "Raw material preparation",
    "Cutting and sawing",
    "Gluing frame",
    "Profiling and milling",
    "Frame assembling",
    "Finishing",
    "Coating and painting",
    "Glazing",
    "Hardware installation",
    "Quality control",
    "Packaging",
    "Outbound logistic",
]

# ---------------------------------------------------------------------------
# MAS — Masonry (typical brick/block production)
# ---------------------------------------------------------------------------

MAS_PROCESS_STEPS: list[str] = [
    "Material procurement",
    "Inbound logistic",
    "Raw material preparation",
    "Mixing and blending",
    "Molding / Extrusion",
    "Drying",
    "Firing / Curing",
    "Quality control",
    "Packaging",
    "Outbound logistic",
]

# ---------------------------------------------------------------------------
# Generic fallback
# ---------------------------------------------------------------------------

GENERIC_PROCESS_STEPS: list[str] = [
    "Material procurement",
    "Inbound logistic",
    "Raw material preparation",
    "Manufacturing / Processing",
    "Quality control",
    "Packaging",
    "Outbound logistic",
]


# ---------------------------------------------------------------------------
# Registry: ProductFamily → process steps
# ---------------------------------------------------------------------------

PROCESS_STEPS: dict[ProductFamily, list[str]] = {
    ProductFamily.DWS: DWS_PROCESS_STEPS,
    ProductFamily.MAS: MAS_PROCESS_STEPS,
}


def get_process_steps(family: ProductFamily) -> list[str]:
    """Get manufacturing process steps for a product family, falling back to generic."""
    return PROCESS_STEPS.get(family, GENERIC_PROCESS_STEPS)
