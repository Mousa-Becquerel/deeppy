"""
Pass 1 output model — Document classification.

The classification agent determines what type of document this is
and which product family it belongs to.
"""

from typing import Optional

from pydantic import BaseModel, Field

from ..ontology.enums import DocumentType, ProductFamily, ConfidenceLevel


class DocumentClassification(BaseModel):
    """Output of Pass 1: classify a single document."""

    document_type: DocumentType = Field(
        ..., description="Detected document type (DoP, EPD, TechnicalSheet, etc.)"
    )
    document_type_confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confidence in document type classification (0.0 to 1.0)"
    )
    product_family: Optional[ProductFamily] = Field(
        None, description="Detected product family code (DWS, MAS, TIP, etc.)"
    )
    product_family_name: Optional[str] = Field(
        None, description="Full name of detected product family"
    )
    product_name: Optional[str] = Field(
        None, description="Product name if identifiable from the document"
    )
    manufacturer: Optional[str] = Field(
        None, description="Manufacturer name if identifiable"
    )
    language: Optional[str] = Field(
        None, description="Primary language of the document (e.g., 'it', 'en', 'de')"
    )
    reference_standard: Optional[str] = Field(
        None, description="Harmonized standard referenced (e.g., 'EN 14351-1', 'EN 771-1')"
    )
    reason: str = Field(
        ..., description="Brief explanation of how the classification was determined"
    )
