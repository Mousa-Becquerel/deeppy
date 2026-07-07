"""
Combined extraction output model — what Pass 2 returns per document.

This is a flat model containing all sections so the LLM can populate
whichever fields are present in the document. Sections that don't apply
to a given document type will remain at their defaults (empty).
"""

from pydantic import BaseModel, Field

from .overview import OverviewSection
from .composition import CompositionSection
from .performance import PerformanceSection
from .compliance import ComplianceSection
from .lifecycle import LifecycleSection


class DocumentExtractionOutput(BaseModel):
    """
    Pass 2 output for a single document.

    The LLM fills whichever sections it finds data for.
    For example, a DoP will populate overview + compliance + performance,
    while an EPD will populate lifecycle + performance + overview.
    """
    overview: OverviewSection = Field(default_factory=OverviewSection)
    composition: CompositionSection = Field(default_factory=CompositionSection)
    performance: PerformanceSection = Field(default_factory=PerformanceSection)
    compliance: ComplianceSection = Field(default_factory=ComplianceSection)
    lifecycle: LifecycleSection = Field(default_factory=LifecycleSection)
