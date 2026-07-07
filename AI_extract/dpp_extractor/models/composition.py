"""
Composition section models — Bill of Materials with supplier logistics.
Maps to ontology: Composition section + Bill_of_materials sheet.
"""

from typing import Optional

from pydantic import BaseModel, Field

from .common import ExtractedField


class SupplierData(BaseModel):
    """Supplier information for a single material."""
    name: ExtractedField[str] = Field(default_factory=ExtractedField)
    address: ExtractedField[str] = Field(default_factory=ExtractedField)
    transport_method: ExtractedField[str] = Field(default_factory=ExtractedField)
    eu_vehicle_class: ExtractedField[str] = Field(default_factory=ExtractedField)
    distance_km: ExtractedField[float] = Field(default_factory=ExtractedField)


class MaterialEntry(BaseModel):
    """A single material/component in the Bill of Materials."""
    material_id: str = Field(..., description="Identifier, e.g. 'Material#1'")
    id_code: ExtractedField[str] = Field(default_factory=ExtractedField)
    description: ExtractedField[str] = Field(default_factory=ExtractedField)
    unit: ExtractedField[str] = Field(default_factory=ExtractedField)
    quantity_per_product: ExtractedField[float] = Field(default_factory=ExtractedField)
    percentage: ExtractedField[float] = Field(
        default_factory=ExtractedField,
        description="Weight or volume percentage of total product"
    )
    origin: ExtractedField[str] = Field(
        default_factory=ExtractedField,
        description="Geographic origin (e.g., 'EU', 'Italy')"
    )
    recyclable: ExtractedField[str] = Field(
        default_factory=ExtractedField,
        description="Whether the material is recyclable"
    )
    suppliers: list[SupplierData] = Field(default_factory=list)


class CompositionSection(BaseModel):
    """Complete Composition section of the DPP."""
    materials: list[MaterialEntry] = Field(default_factory=list)
