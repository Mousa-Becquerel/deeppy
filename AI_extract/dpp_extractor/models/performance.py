"""
Performance section models — family-dynamic performance properties.

Uses a flat List[PerformanceValue] rather than family-specific typed classes.
The extraction prompt is dynamically built from performance_registry.py.
"""

from typing import Optional

from pydantic import BaseModel, Field

from .common import ExtractedField
from ..ontology.enums import PerformanceCategory


class PerformanceValue(BaseModel):
    """A single performance property extracted from documents."""
    property_name: str = Field(
        ..., description="Name of the property (e.g., 'Compressive strength')"
    )
    category: PerformanceCategory = Field(
        ..., description="Category: Mechanical, Thermal, Acoustic, Fire, Durability, Environmental"
    )
    value: ExtractedField[str] = Field(default_factory=ExtractedField)
    unit: Optional[str] = Field(
        None, description="Unit of measurement (e.g., 'N/mm2', 'W/mK')"
    )
    test_standard: Optional[str] = Field(
        None, description="Reference test standard (e.g., 'EN 826', 'EN 12667')"
    )


class PerformanceSection(BaseModel):
    """
    Complete Performance section of the DPP.

    The values list is populated dynamically based on the detected product family.
    The extraction prompt lists the exact properties to look for.
    """
    values: list[PerformanceValue] = Field(default_factory=list)

    def get_by_category(self, category: PerformanceCategory) -> list[PerformanceValue]:
        """Get all performance values for a given category."""
        return [v for v in self.values if v.category == category]

    def get_by_name(self, name: str) -> Optional[PerformanceValue]:
        """Get a performance value by property name (case-insensitive)."""
        name_lower = name.lower()
        for v in self.values:
            if v.property_name.lower() == name_lower:
                return v
        return None

    @property
    def filled_count(self) -> int:
        """Number of performance values that have been filled."""
        return sum(1 for v in self.values if v.value.is_filled)

    @property
    def total_count(self) -> int:
        """Total number of performance values."""
        return len(self.values)
