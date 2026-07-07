"""
Lifecycle section models — A1 through C4 stages with detailed A3 manufacturing.
Maps to ontology: Lifecycle section (LCA stages + A3 manufacturing data).
"""

from typing import Optional

from pydantic import BaseModel, Field

from .common import ExtractedField


class ManufacturingEnergy(BaseModel):
    """A3 energy consumption details."""
    energy_electrical: ExtractedField[float] = Field(default_factory=ExtractedField)  # kWh/yr
    renewable_rate_electrical: ExtractedField[float] = Field(default_factory=ExtractedField)  # %
    onsite_pv: ExtractedField[float] = Field(default_factory=ExtractedField)  # kWh/yr
    energy_thermal: ExtractedField[float] = Field(default_factory=ExtractedField)  # Sm^3
    renewable_rate_thermal: ExtractedField[float] = Field(default_factory=ExtractedField)  # %
    grid_mix: ExtractedField[float] = Field(default_factory=ExtractedField)  # % fossil/renewable


class ManufacturingWaste(BaseModel):
    """A3 waste production entry."""
    material: ExtractedField[str] = Field(default_factory=ExtractedField)
    weight_kg: ExtractedField[float] = Field(default_factory=ExtractedField)


class A3Manufacturing(BaseModel):
    """
    Detailed A3 Manufacturing data from the ontology.

    Covers: reference year, production volume, process description,
    process steps, energy, water, packaging, and waste.
    """
    reference_year: ExtractedField[str] = Field(default_factory=ExtractedField)
    total_production: ExtractedField[float] = Field(default_factory=ExtractedField)
    process_description: ExtractedField[str] = Field(default_factory=ExtractedField)
    process_steps: list[str] = Field(default_factory=list)  # From manufacturing_registry
    # Energy
    energy: ManufacturingEnergy = Field(default_factory=ManufacturingEnergy)
    # Water
    water_use: ExtractedField[float] = Field(default_factory=ExtractedField)  # m^3
    # Packaging
    packaging: ExtractedField[str] = Field(default_factory=ExtractedField)
    # Waste (can have multiple entries)
    waste: list[ManufacturingWaste] = Field(default_factory=list)


class LifecycleStage(BaseModel):
    """
    A single LCA lifecycle stage (A1, A2, A4, A5, B1-B7, C1-C4, D).

    For most stages the extractor only captures the EPD indicator values
    (GWP, ODP, AP, etc.). The detailed breakdown is in A3Manufacturing.
    """
    stage_code: str = Field(..., description="E.g. 'A1', 'B2', 'C3'")
    description: ExtractedField[str] = Field(default_factory=ExtractedField)
    gwp_total: ExtractedField[float] = Field(default_factory=ExtractedField)  # kg CO2-eq
    gwp_fossil: ExtractedField[float] = Field(default_factory=ExtractedField)
    gwp_biogenic: ExtractedField[float] = Field(default_factory=ExtractedField)
    gwp_luluc: ExtractedField[float] = Field(default_factory=ExtractedField)
    odp: ExtractedField[float] = Field(default_factory=ExtractedField)  # kg CFC-11-eq
    ap: ExtractedField[float] = Field(default_factory=ExtractedField)  # mol H+-eq
    ep_freshwater: ExtractedField[float] = Field(default_factory=ExtractedField)  # kg P-eq
    ep_marine: ExtractedField[float] = Field(default_factory=ExtractedField)  # kg N-eq
    pocp: ExtractedField[float] = Field(default_factory=ExtractedField)  # kg NMVOC-eq
    adp_minerals: ExtractedField[float] = Field(default_factory=ExtractedField)  # kg Sb-eq
    adp_fossil: ExtractedField[float] = Field(default_factory=ExtractedField)  # MJ
    wdp: ExtractedField[float] = Field(default_factory=ExtractedField)  # m^3 world-eq


# Standard EPD lifecycle stage codes
STAGE_CODES = [
    "A1", "A2", "A3", "A4", "A5",
    "B1", "B2", "B3", "B4", "B5", "B6", "B7",
    "C1", "C2", "C3", "C4",
    "D",
]


class LifecycleSection(BaseModel):
    """Complete Lifecycle section of the DPP."""
    # Detailed A3 manufacturing data (primary extraction target)
    a3_manufacturing: A3Manufacturing = Field(default_factory=A3Manufacturing)
    # EPD environmental indicators per stage (extracted from EPD documents)
    stages: list[LifecycleStage] = Field(default_factory=list)

    def get_stage(self, code: str) -> Optional[LifecycleStage]:
        """Get a specific lifecycle stage by code."""
        for stage in self.stages:
            if stage.stage_code == code:
                return stage
        return None

    def get_stages_by_module(self, prefix: str) -> list[LifecycleStage]:
        """Get all stages starting with a prefix, e.g. 'A' or 'C'."""
        return [s for s in self.stages if s.stage_code.startswith(prefix)]
