"""
Product-family-specific performance fields from DeePPy_data_ontology.xlsx — Performance sheet.

Each product family has its own set of performance properties to extract.
The AI prompt is dynamically built from this registry.
"""

from dataclasses import dataclass
from typing import Optional

from .enums import ProductFamily, PerformanceCategory


@dataclass(frozen=True)
class PerformanceField:
    """A single performance property to extract for a product family."""
    name: str                           # Display name (e.g., "Compressive strength")
    category: PerformanceCategory       # Mechanical, Thermal, etc.
    unit: Optional[str] = None          # Expected unit (e.g., "N/mm2", "W/mK")
    test_standard: Optional[str] = None # Reference EN standard if known


# ---------------------------------------------------------------------------
# DWS — Doors, Windows, Shutters
# ---------------------------------------------------------------------------

DWS_PERFORMANCE: list[PerformanceField] = [
    # Mechanical (Air permeability moved to Durability per new ontology)
    PerformanceField("Resistance to wind load", PerformanceCategory.MECHANICAL, "Class"),
    PerformanceField("Load-bearing capacity", PerformanceCategory.MECHANICAL, "N"),
    PerformanceField("Operating forces", PerformanceCategory.MECHANICAL, "Class"),
    PerformanceField("Impact resistance", PerformanceCategory.MECHANICAL, "J"),
    PerformanceField("Burglary resistance", PerformanceCategory.MECHANICAL, "Class"),
    PerformanceField("Pendulum impact resistance", PerformanceCategory.MECHANICAL, "Class"),
    # Thermal — includes optical fields per EN 14351-1 (light + Psi)
    PerformanceField("Thermal transmittance (Uw)", PerformanceCategory.THERMAL, "W/m2K"),
    PerformanceField("Glass thermal transmittance (Ug)", PerformanceCategory.THERMAL, "W/m2K"),
    PerformanceField("Frame thermal transmittance (Uf)", PerformanceCategory.THERMAL, "W/m2K"),
    PerformanceField("Linear thermal transmittance (Psi)", PerformanceCategory.THERMAL, "W/mK"),
    PerformanceField("Solar factor (g)", PerformanceCategory.THERMAL, "%"),
    PerformanceField("Light transmittance (Tv)", PerformanceCategory.THERMAL, "%"),
    PerformanceField("Light reflectance", PerformanceCategory.THERMAL, "%"),
    PerformanceField("Temperature factor (fRsi)", PerformanceCategory.THERMAL),
    # Acoustic
    PerformanceField("Airborne sound insulation (Rw)", PerformanceCategory.ACOUSTIC, "dB"),
    # Fire
    PerformanceField("Fire resistance classification", PerformanceCategory.FIRE, "Class"),
    PerformanceField("Reaction to fire", PerformanceCategory.FIRE, "Euroclass"),
    # Durability
    PerformanceField("Resistance to repeated opening/closing", PerformanceCategory.DURABILITY),
    PerformanceField("Air permeability", PerformanceCategory.DURABILITY, "Class"),
    PerformanceField("Watertightness", PerformanceCategory.DURABILITY, "Class"),
    PerformanceField("Corrosion resistance", PerformanceCategory.DURABILITY),
    PerformanceField("UV resistance", PerformanceCategory.DURABILITY, "Class"),
    # Environmental (full set per new ontology)
    PerformanceField("Release of dangerous substances (VOC)", PerformanceCategory.ENVIRONMENTAL),
    PerformanceField("Recycled content", PerformanceCategory.ENVIRONMENTAL, "%"),
    PerformanceField("Circularity index score", PerformanceCategory.ENVIRONMENTAL, "%"),
    PerformanceField("GWP", PerformanceCategory.ENVIRONMENTAL, "kgCO2eq"),
    PerformanceField("Embodied Energy", PerformanceCategory.ENVIRONMENTAL, "MJ"),
    PerformanceField("Embodied Carbon", PerformanceCategory.ENVIRONMENTAL, "kgCO2eq"),
    PerformanceField("Water consumption", PerformanceCategory.ENVIRONMENTAL, "m3"),
]


# ---------------------------------------------------------------------------
# MAS — Masonry and related products
# ---------------------------------------------------------------------------

MAS_PERFORMANCE: list[PerformanceField] = [
    # Mechanical
    PerformanceField("Compressive strength", PerformanceCategory.MECHANICAL, "N/mm2"),
    PerformanceField("Compression resistance (base)", PerformanceCategory.MECHANICAL, "N/mm2"),
    PerformanceField("Compression resistance (head)", PerformanceCategory.MECHANICAL, "N/mm2"),
    PerformanceField("Tensile strength", PerformanceCategory.MECHANICAL, "N/mm2"),
    PerformanceField("Flexural strength", PerformanceCategory.MECHANICAL, "N/mm2"),
    PerformanceField("Elasticity modulus", PerformanceCategory.MECHANICAL, "N/mm2"),
    PerformanceField("Impact resistance", PerformanceCategory.MECHANICAL, "J"),
    PerformanceField("Drilling percentage", PerformanceCategory.MECHANICAL, "%"),
    PerformanceField("Block thickness", PerformanceCategory.MECHANICAL, "mm"),
    PerformanceField("Medium density", PerformanceCategory.MECHANICAL, "kg/m3"),
    # Thermal
    PerformanceField("Thermal conductivity", PerformanceCategory.THERMAL, "W/mK"),
    PerformanceField("Thermal resistance", PerformanceCategory.THERMAL, "m2K/W"),
    PerformanceField("Thermal transmittance (U)", PerformanceCategory.THERMAL, "W/m2K"),
    PerformanceField("Expansion coefficient", PerformanceCategory.THERMAL, "1/K"),
    PerformanceField("Resistance to water vapor diffusion", PerformanceCategory.THERMAL, "μ"),
    PerformanceField("Specific heat", PerformanceCategory.THERMAL, "J/kgK"),
    PerformanceField("Thermal lag", PerformanceCategory.THERMAL, "h"),
    # Acoustic
    PerformanceField("Sound insulation (Rw)", PerformanceCategory.ACOUSTIC, "dB"),
    PerformanceField("Sound absorption", PerformanceCategory.ACOUSTIC, "%"),
    # Fire
    PerformanceField("Fire reaction classification", PerformanceCategory.FIRE, "Euroclass"),
    PerformanceField("Reaction to fire", PerformanceCategory.FIRE, "Euroclass"),
    # Durability
    PerformanceField("Resistance to chemicals or biological agents", PerformanceCategory.DURABILITY, "Class"),
    PerformanceField("Resistance to freeze-thaw cycles", PerformanceCategory.DURABILITY, "Class"),
    PerformanceField("UV resistance", PerformanceCategory.DURABILITY, "Class"),
    PerformanceField("Water absorbtion", PerformanceCategory.DURABILITY, "g/m2"),
    PerformanceField("Soluble active salts content", PerformanceCategory.DURABILITY, "Class"),
    # Environmental (consistent with new ontology — same 7 fields across all families)
    PerformanceField("Release of dangerous substances (VOC)", PerformanceCategory.ENVIRONMENTAL),
    PerformanceField("Recycled content", PerformanceCategory.ENVIRONMENTAL, "%"),
    PerformanceField("Circularity index score", PerformanceCategory.ENVIRONMENTAL, "%"),
    PerformanceField("GWP", PerformanceCategory.ENVIRONMENTAL, "kgCO2eq"),
    PerformanceField("Embodied Energy", PerformanceCategory.ENVIRONMENTAL, "MJ"),
    PerformanceField("Embodied Carbon", PerformanceCategory.ENVIRONMENTAL, "kgCO2eq"),
    PerformanceField("Water consumption", PerformanceCategory.ENVIRONMENTAL, "m3"),
]


# ---------------------------------------------------------------------------
# TIP — Thermal Insulation Products (panels, kits)
# ---------------------------------------------------------------------------

TIP_PERFORMANCE: list[PerformanceField] = [
    # Mechanical
    PerformanceField("Compressive strength", PerformanceCategory.MECHANICAL, "N/mm2"),
    PerformanceField("Tensile strength", PerformanceCategory.MECHANICAL, "N/mm2"),
    PerformanceField("Flexural strength", PerformanceCategory.MECHANICAL, "N/mm2"),
    PerformanceField("Elasticity modulus", PerformanceCategory.MECHANICAL, "N/mm2"),
    PerformanceField("Impact resistance", PerformanceCategory.MECHANICAL, "J"),
    # Thermal
    PerformanceField("Thermal conductivity", PerformanceCategory.THERMAL, "W/mK"),
    PerformanceField("Thermal resistance", PerformanceCategory.THERMAL, "m2K/W"),
    PerformanceField("Expansion coefficient", PerformanceCategory.THERMAL, "1/K"),
    PerformanceField("Permeability to water vapor", PerformanceCategory.THERMAL, "g/m^2*24h"),
    # Acoustic
    PerformanceField("Sound insulation (Rw)", PerformanceCategory.ACOUSTIC, "dB"),
    PerformanceField("Sound absorption", PerformanceCategory.ACOUSTIC, "%"),
    # Fire
    PerformanceField("Fire resistance classification", PerformanceCategory.FIRE, "Class"),
    PerformanceField("Reaction to fire", PerformanceCategory.FIRE, "Euroclass"),
    # Durability
    PerformanceField("Resistance to chemicals or biological agents", PerformanceCategory.DURABILITY, "Class"),
    PerformanceField("Water absorbtion", PerformanceCategory.DURABILITY, "g/m2"),
    # Environmental (full set — consistent across all families)
    PerformanceField("Release of dangerous substances (VOC)", PerformanceCategory.ENVIRONMENTAL),
    PerformanceField("Recycled content", PerformanceCategory.ENVIRONMENTAL, "%"),
    PerformanceField("Circularity index score", PerformanceCategory.ENVIRONMENTAL, "%"),
    PerformanceField("GWP", PerformanceCategory.ENVIRONMENTAL, "kgCO2eq"),
    PerformanceField("Embodied Energy", PerformanceCategory.ENVIRONMENTAL, "MJ"),
    PerformanceField("Embodied Carbon", PerformanceCategory.ENVIRONMENTAL, "kgCO2eq"),
    PerformanceField("Water consumption", PerformanceCategory.ENVIRONMENTAL, "m3"),
]


# ---------------------------------------------------------------------------
# CEM — Cement, building limes, hydraulic binders
# ---------------------------------------------------------------------------

CEM_PERFORMANCE: list[PerformanceField] = [
    # Mechanical
    PerformanceField("Compressive strength", PerformanceCategory.MECHANICAL, "N/mm2"),
    PerformanceField("Tensile strength", PerformanceCategory.MECHANICAL, "N/mm2"),
    PerformanceField("Flexural strength", PerformanceCategory.MECHANICAL, "N/mm2"),
    PerformanceField("Elasticity modulus", PerformanceCategory.MECHANICAL, "N/mm2"),
    # Thermal
    PerformanceField("Thermal conductivity", PerformanceCategory.THERMAL, "W/mK"),
    PerformanceField("Thermal resistance", PerformanceCategory.THERMAL, "m2K/W"),
    PerformanceField("Expansion coefficient", PerformanceCategory.THERMAL, "1/K"),
    PerformanceField("Permeability to water vapor", PerformanceCategory.THERMAL, "g/m^2*24h"),
    # Fire
    PerformanceField("Fire resistance classification", PerformanceCategory.FIRE, "Class"),
    PerformanceField("Reaction to fire", PerformanceCategory.FIRE, "Euroclass"),
    # Durability
    PerformanceField("Resistance to freeze-thaw cycles", PerformanceCategory.DURABILITY, "Class"),
    # Environmental (full set — consistent across all families)
    PerformanceField("Release of dangerous substances (VOC)", PerformanceCategory.ENVIRONMENTAL),
    PerformanceField("Recycled content", PerformanceCategory.ENVIRONMENTAL, "%"),
    PerformanceField("Circularity index score", PerformanceCategory.ENVIRONMENTAL, "%"),
    PerformanceField("GWP", PerformanceCategory.ENVIRONMENTAL, "kgCO2eq"),
    PerformanceField("Embodied Energy", PerformanceCategory.ENVIRONMENTAL, "MJ"),
    PerformanceField("Embodied Carbon", PerformanceCategory.ENVIRONMENTAL, "kgCO2eq"),
    PerformanceField("Water consumption", PerformanceCategory.ENVIRONMENTAL, "m3"),
]


# ---------------------------------------------------------------------------
# Generic fallback for families without specific definitions yet
# ---------------------------------------------------------------------------

GENERIC_PERFORMANCE: list[PerformanceField] = [
    # Mechanical
    PerformanceField("Compressive strength", PerformanceCategory.MECHANICAL),
    PerformanceField("Tensile strength", PerformanceCategory.MECHANICAL),
    PerformanceField("Flexural strength", PerformanceCategory.MECHANICAL),
    PerformanceField("Impact resistance", PerformanceCategory.MECHANICAL),
    # Thermal
    PerformanceField("Thermal conductivity", PerformanceCategory.THERMAL),
    PerformanceField("Thermal resistance", PerformanceCategory.THERMAL),
    # Acoustic
    PerformanceField("Sound insulation (Rw)", PerformanceCategory.ACOUSTIC, "dB"),
    PerformanceField("Sound absorption", PerformanceCategory.ACOUSTIC, "%"),
    # Fire
    PerformanceField("Fire resistance classification", PerformanceCategory.FIRE, "Class"),
    PerformanceField("Reaction to fire", PerformanceCategory.FIRE, "Euroclass"),
    # Durability
    PerformanceField("UV resistance", PerformanceCategory.DURABILITY),
    PerformanceField("Corrosion resistance", PerformanceCategory.DURABILITY),
    PerformanceField("Chemical resistance", PerformanceCategory.DURABILITY),
    PerformanceField("Freeze-thaw resistance", PerformanceCategory.DURABILITY),
    # Environmental (consistent set across all families)
    PerformanceField("Release of dangerous substances (VOC)", PerformanceCategory.ENVIRONMENTAL),
    PerformanceField("Recycled content", PerformanceCategory.ENVIRONMENTAL, "%"),
    PerformanceField("Circularity index score", PerformanceCategory.ENVIRONMENTAL, "%"),
    PerformanceField("GWP", PerformanceCategory.ENVIRONMENTAL, "kgCO2eq"),
    PerformanceField("Embodied Energy", PerformanceCategory.ENVIRONMENTAL, "MJ"),
    PerformanceField("Embodied Carbon", PerformanceCategory.ENVIRONMENTAL, "kgCO2eq"),
    PerformanceField("Water consumption", PerformanceCategory.ENVIRONMENTAL, "m3"),
]


# ---------------------------------------------------------------------------
# Registry: ProductFamily → performance fields
# ---------------------------------------------------------------------------

PERFORMANCE_FIELDS: dict[ProductFamily, list[PerformanceField]] = {
    ProductFamily.DWS: DWS_PERFORMANCE,
    ProductFamily.MAS: MAS_PERFORMANCE,
    ProductFamily.TIP: TIP_PERFORMANCE,
    ProductFamily.CEM: CEM_PERFORMANCE,
    # All other families use the GENERIC_PERFORMANCE fallback.
    # Add specific lists here as the ontology expands to cover more CPR families.
}


def get_performance_fields(family: ProductFamily) -> list[PerformanceField]:
    """Get performance fields for a product family, falling back to generic."""
    return PERFORMANCE_FIELDS.get(family, GENERIC_PERFORMANCE)


def get_performance_fields_by_category(
    family: ProductFamily,
) -> dict[PerformanceCategory, list[PerformanceField]]:
    """Get performance fields grouped by category."""
    fields = get_performance_fields(family)
    grouped: dict[PerformanceCategory, list[PerformanceField]] = {}
    for f in fields:
        grouped.setdefault(f.category, []).append(f)
    return grouped
