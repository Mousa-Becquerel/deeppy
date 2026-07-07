"""
Full Digital Product Passport model — assembles all sections.
This is the top-level output of the extraction pipeline.
"""

from pydantic import BaseModel, Field

from .overview import OverviewSection
from .composition import CompositionSection
from .performance import PerformanceSection
from .compliance import ComplianceSection
from .lifecycle import LifecycleSection
from .documents import DocumentsSection
from ..ontology.enums import ProductFamily, ConfidenceLevel


class PassportMetadata(BaseModel):
    """Extraction metadata — not part of the DPP data itself."""
    product_family: ProductFamily = Field(..., description="Detected product family")
    source_documents: list[str] = Field(default_factory=list, description="Filenames processed")
    extraction_model: str = Field(default="gemini-2.0-flash", description="LLM model used")
    extraction_version: str = Field(default="1.0.0", description="Extractor version")


class DigitalProductPassport(BaseModel):
    """
    Complete DPP matching the DeePPy ontology structure.

    This is the final output of the 3-pass pipeline:
    Pass 1 (classify) → Pass 2 (extract per-doc) → Pass 3 (merge) → this.
    """
    metadata: PassportMetadata
    overview: OverviewSection = Field(default_factory=OverviewSection)
    composition: CompositionSection = Field(default_factory=CompositionSection)
    performance: PerformanceSection = Field(default_factory=PerformanceSection)
    compliance: ComplianceSection = Field(default_factory=ComplianceSection)
    lifecycle: LifecycleSection = Field(default_factory=LifecycleSection)
    documents: DocumentsSection = Field(default_factory=DocumentsSection)

    @property
    def completeness(self) -> float:
        """Calculate overall passport completeness as a percentage."""
        sections = [
            self.overview, self.composition, self.performance,
            self.compliance, self.lifecycle,
        ]
        filled = 0
        total = 0
        for section in sections:
            for field_name, field_info in section.model_fields.items():
                val = getattr(section, field_name)
                if hasattr(val, 'is_filled'):
                    total += 1
                    if val.is_filled:
                        filled += 1
        return (filled / total * 100) if total > 0 else 0.0

    @property
    def fields_needing_review(self) -> list[str]:
        """List field paths that need user review (MEDIUM confidence)."""
        review = []
        for section_name in ["overview", "composition", "performance", "compliance", "lifecycle"]:
            section = getattr(self, section_name)
            for field_name in section.model_fields:
                val = getattr(section, field_name)
                if hasattr(val, 'needs_review') and val.needs_review:
                    review.append(f"{section_name}.{field_name}")
        return review

    def to_frontend_dict(self) -> dict:
        """Serialize to the JSON structure the React frontend expects."""
        return self.model_dump(mode="json")
