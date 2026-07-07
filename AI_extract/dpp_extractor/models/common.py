"""
Core building blocks for the DPP extraction models.

ExtractedField[T] is the fundamental wrapper — every field in the passport
carries its value, confidence, source reference, and optional AI note.
This maps directly to the frontend's EF component props (v, c, s, n).
"""

from typing import TypeVar, Generic, Optional

from pydantic import BaseModel, Field

from ..ontology.enums import ConfidenceLevel, DocumentType, ProductFamily


T = TypeVar("T")


class SourceReference(BaseModel):
    """Where a value was extracted from."""
    document_name: str = Field(
        ..., description="Filename of the source document, e.g. 'DoP-XPS100-2026.pdf'"
    )
    document_type: Optional[DocumentType] = Field(
        None, description="Type of the source document"
    )
    source_family: Optional[ProductFamily] = Field(
        None,
        description="Product family the source document was classified as. "
                    "When this differs from the passport's family, the value came "
                    "from a sub-component document (e.g., glass DoP for a window).",
    )
    page: Optional[int] = Field(
        None, description="Page number where the value was found (1-indexed)"
    )
    snippet: Optional[str] = Field(
        None, description="Brief text excerpt around the extracted value"
    )

    def display(self) -> str:
        """Format for frontend display, e.g. 'DoP-XPS100-2026.pdf, p. 3'"""
        s = self.document_name
        if self.page:
            s += f", p. {self.page}"
        return s


class ExtractedField(BaseModel, Generic[T]):
    """
    A single extracted field value with metadata.

    Maps to the frontend EF component:
      - value  → v prop
      - confidence → c prop (drives the Conf badge color)
      - source → s prop (displayed as "Source: ...")
      - note → n prop (displayed as amber/red annotation below the field)
    """
    value: Optional[T] = Field(
        None, description="The extracted value, or None if not found"
    )
    confidence: ConfidenceLevel = Field(
        ConfidenceLevel.LOW,
        description="Confidence level: high (auto), medium (review), low (missing)"
    )
    source: Optional[SourceReference] = Field(
        None, description="Where this value was extracted from"
    )
    note: Optional[str] = Field(
        None, description="AI explanation or instruction for the user"
    )

    @property
    def is_filled(self) -> bool:
        """Whether this field has a non-empty value."""
        if self.value is None:
            return False
        if isinstance(self.value, str) and not self.value.strip():
            return False
        return True

    @property
    def needs_review(self) -> bool:
        """Whether this field needs user review."""
        return self.confidence == ConfidenceLevel.MEDIUM

    @property
    def is_missing(self) -> bool:
        """Whether this field is missing data."""
        return self.confidence == ConfidenceLevel.LOW and not self.is_filled

    def to_frontend_dict(self) -> dict:
        """Serialize to the format the frontend EF component expects."""
        return {
            "value": self.value if self.is_filled else None,
            "confidence": self.confidence.value,
            "source": self.source.display() if self.source else None,
            "note": self.note,
        }
