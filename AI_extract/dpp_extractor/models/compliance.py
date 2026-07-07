"""
Compliance section models — Declarations, Safety, Certifications.
Maps to ontology: Compliance section (all 10 safety questions + labeling).
"""

from typing import Optional

from pydantic import BaseModel, Field

from .common import ExtractedField


class SafetyInfo(BaseModel):
    """All 10 safety/substance questions from the ontology."""
    contains_cmrs: ExtractedField[str] = Field(default_factory=ExtractedField)
    contains_svhcs: ExtractedField[str] = Field(default_factory=ExtractedField)
    contains_pentane: ExtractedField[str] = Field(default_factory=ExtractedField)
    contains_pfas: ExtractedField[str] = Field(default_factory=ExtractedField)
    has_flame_retardancy: ExtractedField[str] = Field(default_factory=ExtractedField)
    complies_rohs: ExtractedField[str] = Field(default_factory=ExtractedField)
    produces_voc: ExtractedField[str] = Field(default_factory=ExtractedField)
    contains_heavy_metals: ExtractedField[str] = Field(default_factory=ExtractedField)
    contains_asbestos: ExtractedField[str] = Field(default_factory=ExtractedField)
    complies_child_labor: ExtractedField[str] = Field(default_factory=ExtractedField)
    other_declaration: ExtractedField[str] = Field(default_factory=ExtractedField)


class CertificationEntry(BaseModel):
    """A single certification (product or company level)."""
    name: ExtractedField[str] = Field(default_factory=ExtractedField)
    reference_number: ExtractedField[str] = Field(default_factory=ExtractedField)
    issuing_body: ExtractedField[str] = Field(default_factory=ExtractedField)
    valid_until: ExtractedField[str] = Field(default_factory=ExtractedField)
    scope: ExtractedField[str] = Field(default_factory=ExtractedField)


class ComplianceSection(BaseModel):
    """Complete Compliance section of the DPP."""
    # Declarations of Performance & Conformity
    dop_reference: ExtractedField[str] = Field(default_factory=ExtractedField)
    dop_standard: ExtractedField[str] = Field(default_factory=ExtractedField)
    doc_reference: ExtractedField[str] = Field(default_factory=ExtractedField)
    ce_marking: ExtractedField[str] = Field(default_factory=ExtractedField)
    quality_control: ExtractedField[str] = Field(default_factory=ExtractedField)
    # Safety
    safety: SafetyInfo = Field(default_factory=SafetyInfo)
    # Labeling / Certifications
    product_certifications: list[CertificationEntry] = Field(default_factory=list)
    company_certifications: list[CertificationEntry] = Field(default_factory=list)
    other_labels: ExtractedField[str] = Field(default_factory=ExtractedField)
