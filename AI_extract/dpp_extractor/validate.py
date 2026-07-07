"""
Quick smoke test — instantiate every model and verify serialization.
Run with: python -m dpp_extractor.validate
"""

from .ontology.enums import ProductFamily, DocumentType, ConfidenceLevel
from .ontology.fields import FIELD_REGISTRY, REQUIRED_FIELD_COUNT, TOTAL_FIELD_COUNT
from .ontology.performance_registry import get_performance_fields
from .ontology.manufacturing_registry import get_process_steps
from .ontology.bom_schema import BOMEntry, SupplierInfo

from .models import (
    ExtractedField, SourceReference,
    DocumentClassification,
    ProductInfo, Manufacturer, OverviewSection,
    SupplierData, MaterialEntry, CompositionSection,
    PerformanceValue, PerformanceSection,
    SafetyInfo, CertificationEntry, ComplianceSection,
    ManufacturingEnergy, ManufacturingWaste, A3Manufacturing,
    LifecycleStage, LifecycleSection,
    DocumentReference, DocumentsSection,
    PassportMetadata, DigitalProductPassport,
    MergeConflict, MergeResult,
)


def main() -> None:
    print("=== Ontology ===")
    print(f"  Fields: {TOTAL_FIELD_COUNT} total, {REQUIRED_FIELD_COUNT} required")
    print(f"  Product families: {len(ProductFamily)}")
    dws_perf = get_performance_fields(ProductFamily.DWS)
    print(f"  DWS performance fields: {len(dws_perf)}")
    dws_steps = get_process_steps(ProductFamily.DWS)
    print(f"  DWS process steps: {len(dws_steps)}")

    print("\n=== Models ===")

    ef = ExtractedField(value="test", confidence=ConfidenceLevel.HIGH)
    assert ef.is_filled
    assert not ef.needs_review
    print(f"  ExtractedField: OK (is_filled={ef.is_filled})")

    cls = DocumentClassification(
        document_type=DocumentType.TECHNICAL_SHEET,
        document_type_confidence=0.95,
        product_family=ProductFamily.MAS,
        reason="Test instantiation",
    )
    print(f"  DocumentClassification: {cls.document_type.value} / {cls.product_family.value}")

    overview = OverviewSection()
    print(f"  OverviewSection: OK")

    comp = CompositionSection()
    print(f"  CompositionSection: OK")

    perf = PerformanceSection()
    print(f"  PerformanceSection: filled={perf.filled_count}/{perf.total_count}")

    compliance = ComplianceSection()
    print(f"  ComplianceSection: OK")

    lifecycle = LifecycleSection()
    print(f"  LifecycleSection: OK")

    docs = DocumentsSection()
    print(f"  DocumentsSection: OK")

    passport = DigitalProductPassport(
        metadata=PassportMetadata(
            product_family=ProductFamily.DWS,
            source_documents=["test.pdf"],
        )
    )
    print(f"  DigitalProductPassport: completeness={passport.completeness:.1f}%")
    print(f"  Fields needing review: {len(passport.fields_needing_review)}")

    merge = MergeResult()
    print(f"  MergeResult: OK")

    print("\n=== Serialization ===")
    fd = ef.to_frontend_dict()
    print(f"  Frontend dict keys: {list(fd.keys())}")

    full_json = passport.model_dump_json(indent=2)
    print(f"  Full passport JSON: {len(full_json)} chars")

    # Validate pipeline imports (no GCP needed, just import check)
    print("\n=== Pipeline ===")
    from .prompts.classification import CLASSIFICATION_SYSTEM_PROMPT
    print(f"  Classification prompt: {len(CLASSIFICATION_SYSTEM_PROMPT)} chars")

    from .prompts.extraction import build_extraction_prompt
    prompt = build_extraction_prompt(DocumentType.DOP, ProductFamily.DWS, "test.pdf")
    print(f"  DOP+DWS extraction prompt: {len(prompt)} chars")

    from .models.extraction_output import DocumentExtractionOutput
    ext_out = DocumentExtractionOutput()
    print(f"  DocumentExtractionOutput: OK")

    from .pipeline.merge import merge_extractions
    _, merge_res = merge_extractions([], ProductFamily.DWS)
    print(f"  Merge (empty): OK")

    print("\nALL MODELS + PIPELINE VALIDATED SUCCESSFULLY")


if __name__ == "__main__":
    main()
