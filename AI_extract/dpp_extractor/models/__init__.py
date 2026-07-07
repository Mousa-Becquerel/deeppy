"""Pydantic models for DPP extraction pipeline."""

from .common import ExtractedField, SourceReference
from .classification import DocumentClassification
from .overview import ProductInfo, Manufacturer, OverviewSection
from .composition import SupplierData, MaterialEntry, CompositionSection
from .performance import PerformanceValue, PerformanceSection
from .compliance import SafetyInfo, CertificationEntry, ComplianceSection
from .lifecycle import (
    ManufacturingEnergy, ManufacturingWaste, A3Manufacturing,
    LifecycleStage, LifecycleSection,
)
from .documents import DocumentReference, DocumentsSection
from .extraction_output import DocumentExtractionOutput
from .passport import PassportMetadata, DigitalProductPassport
from .merge_result import MergeConflict, MergeResult

__all__ = [
    # Common
    "ExtractedField", "SourceReference",
    # Classification (Pass 1)
    "DocumentClassification",
    # Overview
    "ProductInfo", "Manufacturer", "OverviewSection",
    # Composition (BoM)
    "SupplierData", "MaterialEntry", "CompositionSection",
    # Performance
    "PerformanceValue", "PerformanceSection",
    # Compliance
    "SafetyInfo", "CertificationEntry", "ComplianceSection",
    # Lifecycle
    "ManufacturingEnergy", "ManufacturingWaste", "A3Manufacturing",
    "LifecycleStage", "LifecycleSection",
    # Documents
    "DocumentReference", "DocumentsSection",
    # Passport (top-level)
    "PassportMetadata", "DigitalProductPassport",
    # Merge
    "MergeConflict", "MergeResult",
]
