"""Item 1 — variant detection from performance rows.

Client canonical case: brick DoP declares 5 thicknesses. Extraction faithfully
produces one perf row per thickness, so the UI would show 5x every metric.
Detector should surface the thickness qualifiers so the UI can filter by SKU.
"""
from __future__ import annotations

from dpp_extractor.models.common import ExtractedField
from dpp_extractor.models.passport import DigitalProductPassport, PassportMetadata
from dpp_extractor.models.performance import PerformanceSection, PerformanceValue
from dpp_extractor.ontology.enums import PerformanceCategory, ProductFamily
from dpp_extractor.pipeline.variant_detect import (
    detect_variants,
    populate_detected_variants,
    _strip_qualifier,
)


def _passport(perf_rows: list[tuple[str, str]]) -> DigitalProductPassport:
    """Build a minimal passport with the given (property_name, value) rows."""
    return DigitalProductPassport(
        metadata=PassportMetadata(product_family=ProductFamily.MAS),
        performance=PerformanceSection(
            values=[
                PerformanceValue(
                    property_name=name,
                    category=PerformanceCategory.THERMAL,
                    value=ExtractedField[str](value=val),
                )
                for name, val in perf_rows
            ]
        ),
    )


# ── helpers ────────────────────────────────────────────────────────────────


def test_strip_qualifier_extracts_trailing_paren():
    base, qual = _strip_qualifier("Thermal transmittance (Uw) (window, 1 leaf)")
    assert base == "Thermal transmittance (Uw)"
    assert qual == "window, 1 leaf"


def test_strip_qualifier_filters_unit_labels():
    """(Uw) alone is a unit-like label, not a variant. Should NOT be extracted."""
    base, qual = _strip_qualifier("Thermal transmittance (Uw)")
    assert qual is None


def test_strip_qualifier_no_parens():
    base, qual = _strip_qualifier("Compressive strength")
    assert base == "Compressive strength"
    assert qual is None


# ── detection ──────────────────────────────────────────────────────────────


def test_detects_variants_across_multiple_properties():
    """Qualifier '(25 cm)' appears on 3 different properties → real variant."""
    p = _passport([
        ("Thermal transmittance (25 cm)", "0.30"),
        ("Sound insulation (25 cm)", "45"),
        ("Compressive strength (25 cm)", "20"),
        ("Thermal transmittance (30 cm)", "0.25"),
        ("Sound insulation (30 cm)", "48"),
        ("Compressive strength (30 cm)", "22"),
    ])
    variants = detect_variants(p)
    assert set(variants) == {"25 cm", "30 cm"}


def test_ignores_single_property_qualifier():
    """(low-e coating) appears on ONLY glass row → not a SKU variant, ignored."""
    p = _passport([
        ("Thermal transmittance (25 cm)", "0.30"),
        ("Sound insulation (25 cm)", "45"),
        ("Thermal transmittance (30 cm)", "0.25"),
        ("Sound insulation (30 cm)", "48"),
        ("Solar factor (low-e coating)", "0.4"),   # only 1 base — filtered
    ])
    variants = detect_variants(p)
    assert set(variants) == {"25 cm", "30 cm"}
    assert "low-e coating" not in variants


def test_no_variants_when_all_rows_unique_qualifier():
    """When every qualifier appears on only 1 property, none are variants."""
    p = _passport([
        ("Thermal transmittance (Uw)", "0.30"),   # unit label — filtered
        ("Sound insulation (Rw)", "45"),           # unit label — filtered
        ("Compressive strength (class)", "20"),    # non-variant word — filtered
    ])
    assert detect_variants(p) == []


def test_orders_by_coverage_then_frequency():
    """Variant covering more properties comes first."""
    p = _passport([
        # variant A covers 3 base properties
        ("Thermal transmittance (A)", "1"),
        ("Sound insulation (A)", "2"),
        ("Compressive strength (A)", "3"),
        # variant B covers 2 base properties
        ("Thermal transmittance (B)", "1"),
        ("Sound insulation (B)", "2"),
    ])
    variants = detect_variants(p)
    assert variants == ["A", "B"]


def test_populate_writes_to_metadata():
    p = _passport([
        ("Thermal transmittance (25 cm)", "0.30"),
        ("Sound insulation (25 cm)", "45"),
        ("Thermal transmittance (30 cm)", "0.25"),
        ("Sound insulation (30 cm)", "48"),
    ])
    populate_detected_variants(p)
    assert set(p.metadata.detected_variants) == {"25 cm", "30 cm"}


def test_populate_noop_when_empty():
    """No perf rows → no variants → metadata list stays empty, no crash."""
    p = _passport([])
    populate_detected_variants(p)
    assert p.metadata.detected_variants == []


def test_selected_variant_default_none():
    p = _passport([])
    assert p.metadata.selected_variant is None


def test_case_preserved_but_dedup_case_insensitive_bases():
    """Base names compared case-insensitively when checking multi-property spread."""
    p = _passport([
        ("Thermal transmittance (25 cm)", "0.30"),
        ("thermal transmittance (25 cm)", "0.30"),   # same base — different case
        ("Sound insulation (25 cm)", "45"),
    ])
    # Only 2 distinct case-insensitive bases → still counts as variant across
    # multiple properties, so "25 cm" surfaces.
    variants = detect_variants(p)
    assert variants == ["25 cm"]
