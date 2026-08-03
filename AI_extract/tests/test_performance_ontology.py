"""Item 6 — Performance ontology enforcement.

Every extracted performance value carries an `is_expected` bool set from the
normalizer's `matched` flag. The frontend uses this to split known spec values
from AI noise (ambient temperature, packaging weight, etc.) into a collapsed
"Other properties" section.

Contract:
    • Fields that longest-prefix-match an entry in performance_registry
      (family list OR GENERIC fallback) → is_expected=True.
    • Fields the normalizer doesn't recognize → is_expected=False, kept but
      surfaced separately in the UI.
    • Legacy passports without the flag → default True (backward compat).
    • Merge across docs: any candidate marked expected → winner is expected.
"""
from __future__ import annotations

import pytest

from dpp_extractor.models.common import ExtractedField
from dpp_extractor.models.performance import PerformanceValue, PerformanceSection
from dpp_extractor.ontology.enums import (
    ConfidenceLevel, DocumentType, PerformanceCategory, ProductFamily,
)
from dpp_extractor.ontology.performance_normalizer import normalize_property_name


# ─── Normalizer basis ─────────────────────────────────────────────────────

def test_normalizer_matched_true_for_family_field():
    """Compressive strength is in the CEM family registry."""
    result = normalize_property_name(
        "Compressive strength", ProductFamily.CEM, PerformanceCategory.MECHANICAL
    )
    assert result.matched is True
    assert "Compressive strength" in result.canonical


def test_normalizer_matched_true_for_generic_field():
    """GWP is in GENERIC_PERFORMANCE — matches on any family."""
    result = normalize_property_name(
        "GWP total", ProductFamily.OTH, PerformanceCategory.ENVIRONMENTAL
    )
    assert result.matched is True


def test_normalizer_matched_false_for_unknown_field():
    """Ambient temperature isn't in any list — the exact client-reported case."""
    result = normalize_property_name(
        "Ambient temperature", ProductFamily.CEM, PerformanceCategory.OTHER
    )
    assert result.matched is False


def test_normalizer_matched_false_for_packaging_weight():
    result = normalize_property_name(
        "Pallet weight", ProductFamily.CEM, PerformanceCategory.OTHER
    )
    assert result.matched is False


# ─── Model default (legacy compat) ────────────────────────────────────────

def test_performance_value_defaults_is_expected_true():
    """Legacy passports serialized before this flag existed round-trip cleanly
    as `is_expected=True` — they render in the main section, not 'Other'."""
    pv = PerformanceValue(
        property_name="Compressive strength",
        category=PerformanceCategory.MECHANICAL,
        value=ExtractedField(value="10", confidence=ConfidenceLevel.HIGH),
        unit="N/mm²",
    )
    assert pv.is_expected is True


def test_performance_value_deserializes_missing_flag_as_true():
    """Explicit missing-field behaviour: JSON payload without is_expected
    (from an older passport in the DB) must default to True."""
    pv = PerformanceValue.model_validate({
        "property_name": "Any",
        "category": "Mechanical",
        "value": {"value": "1", "confidence": "high"},
    })
    assert pv.is_expected is True


def test_performance_value_can_be_false():
    pv = PerformanceValue(
        property_name="Ambient temperature",
        category=PerformanceCategory.OTHER,
        value=ExtractedField(value="8°C", confidence=ConfidenceLevel.MEDIUM),
        is_expected=False,
    )
    assert pv.is_expected is False


# ─── End-to-end: build_passport wires the flag correctly ──────────────────

def _make_simple(**perf_rows):
    """Build a minimal SimpleExtractionOutput with the given performance rows.
    Kwarg = property_name; value = (category, unit)."""
    from dpp_extractor.models.simple_extraction import SimpleExtractionOutput
    payload = {
        "overview": {"product_info": {}, "manufacturer": {}},
        "composition": {},
        "performance": {"values": [
            {"property_name": name, "category": meta[0], "value": "10", "unit": meta[1]}
            for name, meta in perf_rows.items()
        ]},
        "compliance": {"safety": {}},
        "lifecycle": {},
    }
    return SimpleExtractionOutput.model_validate(payload)


def test_map_to_extraction_output_sets_is_expected_from_normalizer():
    """The extract.py mapper pipes normalizer.matched into is_expected."""
    from dpp_extractor.pipeline.extract import _map_to_extraction_output
    simple = _make_simple(**{
        "Compressive strength": ("Mechanical", "N/mm²"),           # known
        "Ambient temperature during transport": ("Other", ""),      # client's bad case
        "Pallet weight": ("Other", "kg"),                           # noise
    })
    result = _map_to_extraction_output(
        simple=simple, doc_name="test.pdf",
        doc_type=DocumentType.TECHNICAL_SHEET, classification=None,
        consensus_family=ProductFamily.CEM,
    )
    by_name = {}
    for pv in result.performance.values:
        # canonical name may be prefixed with a variant; match by containment
        by_name.setdefault(pv.property_name.lower(), pv)

    known = next((pv for name, pv in by_name.items() if "compressive" in name), None)
    ambient = next((pv for name, pv in by_name.items() if "ambient" in name), None)
    pallet = next((pv for name, pv in by_name.items() if "pallet" in name), None)

    assert known is not None and known.is_expected is True, \
        f"Compressive strength should be expected; got {known}"
    assert ambient is not None and ambient.is_expected is False, \
        f"Ambient temp should NOT be expected; got {ambient}"
    assert pallet is not None and pallet.is_expected is False, \
        f"Pallet weight should NOT be expected; got {pallet}"


# ─── Merge propagation ────────────────────────────────────────────────────

def _extraction_with_perf(prop_name: str, category: PerformanceCategory, is_expected: bool):
    """Minimal DocumentExtractionOutput carrying one performance row."""
    from dpp_extractor.models.extraction_output import DocumentExtractionOutput
    from dpp_extractor.models.overview import OverviewSection
    from dpp_extractor.models.composition import CompositionSection
    from dpp_extractor.models.compliance import ComplianceSection
    from dpp_extractor.models.lifecycle import LifecycleSection
    return DocumentExtractionOutput(
        overview=OverviewSection(),
        composition=CompositionSection(),
        performance=PerformanceSection(values=[
            PerformanceValue(
                property_name=prop_name, category=category,
                value=ExtractedField(value="10", confidence=ConfidenceLevel.HIGH),
                unit="N/mm²", is_expected=is_expected,
            ),
        ]),
        compliance=ComplianceSection(),
        lifecycle=LifecycleSection(),
    )


def _dop_cls():
    from dpp_extractor.models.classification import DocumentClassification
    return DocumentClassification(
        document_type=DocumentType.DOP, document_type_confidence=1.0,
        product_family=ProductFamily.CEM, reason="test fixture",
    )


def _ts_cls():
    from dpp_extractor.models.classification import DocumentClassification
    return DocumentClassification(
        document_type=DocumentType.TECHNICAL_SHEET, document_type_confidence=1.0,
        product_family=ProductFamily.CEM, reason="test fixture",
    )


def test_merge_preserves_is_expected_from_any_candidate():
    """When the same property comes from 2 docs and at least one marked it
    expected, the merged winner must be expected. Prevents a single doc's
    misclassification from silently exiling a legit field."""
    from dpp_extractor.pipeline.merge import merge_extractions

    ext_a = _extraction_with_perf(
        "Compressive strength", PerformanceCategory.MECHANICAL, is_expected=True,
    )
    ext_b = _extraction_with_perf(
        "Compressive strength", PerformanceCategory.MECHANICAL, is_expected=False,
    )
    merged, _ = merge_extractions(
        [(ext_a, _dop_cls(), "a.pdf"), (ext_b, _ts_cls(), "b.pdf")],
        ProductFamily.CEM,
    )
    winners = [pv for pv in merged.performance.values
               if pv.property_name.lower() == "compressive strength"]
    assert len(winners) == 1, f"expected 1 merged winner, got {len(winners)}"
    assert winners[0].is_expected is True, "any-expected-wins rule violated"


def test_merge_keeps_false_when_all_candidates_false():
    """Symmetric — no candidate is expected → winner stays not-expected."""
    from dpp_extractor.pipeline.merge import merge_extractions

    ext_a = _extraction_with_perf(
        "Pallet weight", PerformanceCategory.OTHER, is_expected=False,
    )
    ext_b = _extraction_with_perf(
        "Pallet weight", PerformanceCategory.OTHER, is_expected=False,
    )
    merged, _ = merge_extractions(
        [(ext_a, _dop_cls(), "a.pdf"), (ext_b, _ts_cls(), "b.pdf")],
        ProductFamily.CEM,
    )
    winners = [pv for pv in merged.performance.values
               if pv.property_name.lower() == "pallet weight"]
    assert len(winners) == 1
    assert winners[0].is_expected is False
