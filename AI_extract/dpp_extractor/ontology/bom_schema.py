"""
Bill of Materials structure from DeePPy_data_ontology.xlsx — Bill_of_materials sheet.

Defines the per-material row structure including supplier logistics data.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SupplierInfo:
    """Supplier details for a single material in the BoM."""
    name: Optional[str] = None
    address: Optional[str] = None
    transport_method: Optional[str] = None  # Maps to TransportMethod enum
    eu_vehicle_class: Optional[str] = None  # Maps to EUVehicleClass enum
    distance_km: Optional[float] = None


@dataclass
class BOMEntry:
    """
    A single row in the Bill of Materials.

    Matches the ontology columns:
    ID code | Description | Unit | Quantity (per product) | Supplier 1..N
    """
    material_id: str                                    # e.g., "Material#1"
    id_code: Optional[str] = None                       # Internal material code
    description: Optional[str] = None                   # e.g., "Wooden frame"
    unit: Optional[str] = None                          # e.g., "kg", "m2", "pcs"
    quantity_per_product: Optional[float] = None         # Amount per functional unit
    suppliers: list[SupplierInfo] = field(default_factory=list)  # Up to N suppliers


# Example materials from the ontology (DWS window product)
DWS_EXAMPLE_MATERIALS: list[str] = [
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
