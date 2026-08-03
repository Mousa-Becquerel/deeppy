"""Family reconciliation — composition ingredients override the classifier.

Client's canonical bad case: BIO-MORTAR (calce idraulica + biochar as main
ingredients) got classified as PTA (pipes/tanks) instead of CEM. The
reconciler catches this once composition is extracted.
"""
from __future__ import annotations

from dpp_extractor.models.common import ExtractedField
from dpp_extractor.models.composition import CompositionSection, MaterialEntry
from dpp_extractor.models.overview import OverviewSection
from dpp_extractor.models.compliance import ComplianceSection
from dpp_extractor.models.lifecycle import LifecycleSection
from dpp_extractor.models.passport import DigitalProductPassport, PassportMetadata
from dpp_extractor.models.performance import PerformanceSection, PerformanceValue
from dpp_extractor.ontology.enums import (
    ConfidenceLevel, PerformanceCategory, ProductFamily,
)
from dpp_extractor.pipeline.family_reconcile import (
    reconcile_family, suggest_family_from_materials,
)


def _mat(desc: str, i: int = 1) -> MaterialEntry:
    return MaterialEntry(
        material_id=f"Material#{i}",
        description=ExtractedField(value=desc, confidence=ConfidenceLevel.HIGH),
    )


def _passport(materials: list[str], perf: list[tuple[str, PerformanceCategory, bool]] | None = None,
              family: ProductFamily = ProductFamily.OTH) -> DigitalProductPassport:
    return DigitalProductPassport(
        metadata=PassportMetadata(product_family=family, source_documents=[]),
        overview=OverviewSection(),
        composition=CompositionSection(materials=[_mat(m, i) for i, m in enumerate(materials, 1)]),
        performance=PerformanceSection(values=[
            PerformanceValue(
                property_name=name, category=cat,
                value=ExtractedField(value="1", confidence=ConfidenceLevel.HIGH),
                is_expected=is_expected,
            ) for (name, cat, is_expected) in (perf or [])
        ]),
        compliance=ComplianceSection(),
        lifecycle=LifecycleSection(),
    )


# ─── The canonical bad case ───────────────────────────────────────────────

def test_bio_mortar_pta_gets_overridden_to_cem():
    """The exact BIO-MORTAR case: calce + biochar → CEM, not PTA."""
    pp = _passport(
        materials=["Calce idraulica", "Biochar (0-1 mm)",
                   "Nocciolino di oliva (0.5-3mm)", "Acqua"],
        family=ProductFamily.PTA,
    )
    result = reconcile_family(pp, ProductFamily.PTA)
    assert result == ProductFamily.CEM
    assert pp.metadata.product_family == ProductFamily.CEM


def test_bio_mortar_renormalizes_performance_rows():
    """After override, performance rows should be re-normalized: any that
    match the CEM ontology flip from is_expected=False to True."""
    pp = _passport(
        materials=["Calce idraulica", "Biochar"],
        family=ProductFamily.PTA,
        perf=[
            # "Compressive strength" IS in the CEM registry (was False under
            # PTA-generic before override, should flip to True).
            ("Compressive strength", PerformanceCategory.MECHANICAL, False),
            # "Ambient temperature" is not in ANY registry — stays False.
            ("Ambient temperature", PerformanceCategory.OTHER, False),
        ],
    )
    reconcile_family(pp, ProductFamily.PTA)
    by_name = {pv.property_name: pv for pv in pp.performance.values}
    assert by_name["Compressive strength"].is_expected is True, \
        "Compressive strength should be recognized under CEM"
    assert by_name["Ambient temperature"].is_expected is False, \
        "Ambient temperature should still be unrecognized"


# ─── Guardrails: don't override on weak/tied evidence ─────────────────────

def test_single_keyword_hit_below_threshold_no_override():
    """1 hit isn't enough — could be coincidental prose mention."""
    pp = _passport(
        materials=["Polyurethane profile with EPDM gasket"],  # only 'EPDM' hits
        family=ProductFamily.DWS,   # classifier said windows — plausible
    )
    result = reconcile_family(pp, ProductFamily.DWS)
    assert result == ProductFamily.DWS   # kept


def test_no_material_matches_no_override():
    """Ingredients that don't match any registry keyword → keep classifier's call."""
    pp = _passport(
        materials=["Something exotic", "Nothing familiar"],
        family=ProductFamily.OTH,
    )
    result = reconcile_family(pp, ProductFamily.OTH)
    assert result == ProductFamily.OTH


def test_no_materials_no_override():
    """Empty composition → nothing to reason about → keep current family."""
    pp = _passport(materials=[], family=ProductFamily.DWS)
    result = reconcile_family(pp, ProductFamily.DWS)
    assert result == ProductFamily.DWS


def test_classifier_and_ingredients_agree_no_change():
    """If classifier + ingredients agree, no override + no metadata mutation
    surprise. Just confirms the family."""
    pp = _passport(
        materials=["Calce idraulica", "Calce naturale"],
        family=ProductFamily.CEM,
    )
    result = reconcile_family(pp, ProductFamily.CEM)
    assert result == ProductFamily.CEM


# ─── Other override scenarios ─────────────────────────────────────────────

def test_masonry_units_override_cem():
    """A brick DoP mistakenly classified as CEM → MAS."""
    pp = _passport(
        materials=["Blocco in laterizio portante", "Mattone forato"],
        family=ProductFamily.CEM,
    )
    result = reconcile_family(pp, ProductFamily.CEM)
    assert result == ProductFamily.MAS


def test_insulation_boards_override():
    pp = _passport(
        materials=["Polistirene espanso", "Lana di roccia"],
        family=ProductFamily.OTH,
    )
    result = reconcile_family(pp, ProductFamily.OTH)
    assert result == ProductFamily.TIP


# ─── The pure suggest helper (introspection for the logs) ────────────────-

def test_suggest_returns_evidence_dict():
    pp = _passport(
        materials=["Calce idraulica", "Cemento portland"],
        family=ProductFamily.OTH,
    )
    suggested, evidence = suggest_family_from_materials(pp)
    assert suggested == ProductFamily.CEM
    assert ProductFamily.CEM in evidence
    kws = [kw for kw, _ in evidence[ProductFamily.CEM]]
    assert any("calce idraulica" in k for k in kws)
    assert any("portland cement" in k or "cemento portland" in k for k in kws)
