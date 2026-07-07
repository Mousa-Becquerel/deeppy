"""
Merge result model — tracks how cross-document merging was performed.
Used by Pass 3 to record conflict resolution decisions.
"""

from typing import Optional

from pydantic import BaseModel, Field

from ..ontology.enums import DocumentType, ConfidenceLevel


class MergeConflict(BaseModel):
    """Records a conflict where multiple documents provided different values."""
    field_path: str = Field(..., description="Dot-path to the field, e.g. 'overview.product_info.weight'")
    values: list[dict] = Field(
        default_factory=list,
        description="List of {document, value, confidence} from each source",
    )
    resolved_value: Optional[str] = Field(None, description="The chosen value")
    resolved_source: Optional[DocumentType] = Field(None, description="Which document won")
    resolution_reason: str = Field(
        default="", description="Why this source was preferred (e.g. 'DoP has higher authority for performance')"
    )


class MergeResult(BaseModel):
    """
    Output of Pass 3 — merge and reconciliation across documents.

    Tracks which documents contributed, any conflicts found, and
    the final confidence distribution.
    """
    documents_merged: list[str] = Field(default_factory=list, description="Filenames that were merged")
    conflicts: list[MergeConflict] = Field(default_factory=list)
    total_fields_filled: int = Field(default=0)
    total_fields: int = Field(default=0)
    confidence_distribution: dict[str, int] = Field(
        default_factory=lambda: {"high": 0, "medium": 0, "low": 0},
        description="Count of fields at each confidence level",
    )

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    @property
    def completeness_pct(self) -> float:
        return (self.total_fields_filled / self.total_fields * 100) if self.total_fields > 0 else 0.0
