"""
Documents section model — Technical documentation references.
Maps to ontology: Technical Documentation section.
"""

from typing import Optional

from pydantic import BaseModel, Field

from .common import ExtractedField


class DocumentReference(BaseModel):
    """A reference to an uploaded/linked document."""
    filename: str = Field(..., description="Original filename")
    file_type: ExtractedField[str] = Field(default_factory=ExtractedField)  # PDF, DWG, IFC, etc.
    url: Optional[str] = Field(None, description="Link if externally hosted")
    description: ExtractedField[str] = Field(default_factory=ExtractedField)


class DocumentsSection(BaseModel):
    """Complete Documents section of the DPP."""
    # Drawings
    drawing_2d: list[DocumentReference] = Field(default_factory=list)
    drawing_3d: list[DocumentReference] = Field(default_factory=list)
    # Method Statements & Guidelines
    method_statement_installation: list[DocumentReference] = Field(default_factory=list)
    method_statement_maintenance: list[DocumentReference] = Field(default_factory=list)
    method_statement_replacement: list[DocumentReference] = Field(default_factory=list)
    method_statement_dismantling: list[DocumentReference] = Field(default_factory=list)
    # Technical sheets
    technical_data_sheet: list[DocumentReference] = Field(default_factory=list)
    brochure: list[DocumentReference] = Field(default_factory=list)
    other_documents: list[DocumentReference] = Field(default_factory=list)
