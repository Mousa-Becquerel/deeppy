"""Grounding guard — blanks AI-fabricated string values that don't appear
in the source documents.

The canonical case (client report): AI returned "Via Cavour 2 (MN)" as the
manufacturer address, marked it high-confidence, and the frontend rendered
it as a verified green field — but that string never appeared in any
uploaded document. We want the guard to blank it (with an explanatory note)
before it reaches the UI.
"""
from __future__ import annotations

import io
from pathlib import Path

import pytest

from dpp_extractor.models.common import ExtractedField, SourceReference
from dpp_extractor.models.passport import DigitalProductPassport
from dpp_extractor.ontology.enums import ConfidenceLevel, DocumentType, ProductFamily
from dpp_extractor.pipeline.grounding import (
    _normalize,
    build_corpus,
    verify_grounded_strings,
)


def _make_pdf(text: str) -> bytes:
    """Return a real one-page PDF whose visible text is `text`. Used to
    build a corpus the grounding check will read exactly like a real upload."""
    from pypdf import PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    # reportlab draws real text; pdfplumber then reads it back verbatim.
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    y = 800
    for line in text.split("\n"):
        c.drawString(50, y, line)
        y -= 15
    c.showPage()
    c.save()
    return buf.getvalue()


def _passport_with_manufacturer(*, address: str | None, company: str | None) -> DigitalProductPassport:
    """Build a minimal passport carrying the given (AI-produced) manufacturer
    values so we can assert what grounding does to them."""
    from dpp_extractor.pipeline.merge import merge_extractions
    pp, _ = merge_extractions([], ProductFamily.OTH)
    if address is not None:
        pp.overview.manufacturer.address = ExtractedField(
            value=address, confidence=ConfidenceLevel.HIGH,
            source=SourceReference(document_name="fake.pdf"),
        )
    if company is not None:
        pp.overview.manufacturer.company_name = ExtractedField(
            value=company, confidence=ConfidenceLevel.HIGH,
            source=SourceReference(document_name="fake.pdf"),
        )
    return pp


# ─── Normalization ────────────────────────────────────────────────────────

def test_normalize_strips_accents_case_and_punct():
    assert _normalize("Via Emilia 42, 47921 Rimini (RN), Italia") == "viaemilia4247921riminirnitalia"
    assert _normalize("Ediltech S.r.l.") == "ediltechsrl"
    assert _normalize("  ") == ""
    assert _normalize("") == ""


# ─── Corpus building ──────────────────────────────────────────────────────

def test_build_corpus_reads_real_pdf(tmp_path):
    reportlab = pytest.importorskip("reportlab")  # noqa: F841
    p = tmp_path / "doc.pdf"
    p.write_bytes(_make_pdf("Ediltech Srl\nVia Emilia 42, 47921 Rimini"))
    corpus = build_corpus([p])
    assert "ediltechsrl" in corpus
    assert "viaemilia4247921rimini" in corpus


def test_build_corpus_skips_non_pdfs(tmp_path):
    p = tmp_path / "notes.txt"
    p.write_text("Via Cavour 2 (MN)")   # not a PDF — must not join corpus
    assert build_corpus([p]) == ""


def test_build_corpus_handles_missing_files(tmp_path):
    assert build_corpus([tmp_path / "nope.pdf"]) == ""


# ─── The client-reported case ─────────────────────────────────────────────

def test_hallucinated_address_gets_blanked(tmp_path):
    """The exact scenario from the client feedback."""
    pytest.importorskip("reportlab")
    # Real doc mentions the company but NOT any address.
    p = tmp_path / "dop.pdf"
    p.write_bytes(_make_pdf(
        "DECLARATION OF PERFORMANCE\n"
        "Manufacturer: Ediltech Srl\n"
        "Product: XPS Panel 100mm\n"
        "Standard: EN 13164:2012\n"
    ))
    pp = _passport_with_manufacturer(
        address="Via Cavour 2 (MN)",       # fabricated by the AI
        company="Ediltech Srl",             # legitimately in the doc
    )

    stats = verify_grounded_strings(pp, [p])

    # The fake address is gone
    addr = pp.overview.manufacturer.address
    assert addr.value is None, f"Expected None, got {addr.value!r}"
    assert addr.confidence == ConfidenceLevel.LOW
    assert "grounding check" in (addr.note or "").lower()
    assert "Via Cavour 2 (MN)" in (addr.note or ""), "Note should quote what was blanked"

    # The legit company name survived
    assert pp.overview.manufacturer.company_name.value == "Ediltech Srl"
    assert pp.overview.manufacturer.company_name.confidence == ConfidenceLevel.HIGH

    # Stats reflect one blanking
    assert stats["blanked"] >= 1
    assert stats["corpus_chars"] > 0


def test_partial_match_survives_variant_punctuation(tmp_path):
    """`Ediltech S.r.l.` (AI, with dots) should survive when the doc says
    `Ediltech Srl` (no dots) — same tokens after normalization."""
    pytest.importorskip("reportlab")
    p = tmp_path / "doc.pdf"
    p.write_bytes(_make_pdf("Company: Ediltech Srl\nStandard: EN 13164"))
    pp = _passport_with_manufacturer(address=None, company="Ediltech S.r.l.")

    verify_grounded_strings(pp, [p])
    assert pp.overview.manufacturer.company_name.value == "Ediltech S.r.l.", \
        "Punctuation variants of the same company should NOT be blanked"


def test_short_values_are_exempt(tmp_path):
    """Values shorter than the min-guarded-length threshold aren't checked —
    a 3-char company name would match half the corpus by accident."""
    pytest.importorskip("reportlab")
    p = tmp_path / "doc.pdf"
    p.write_bytes(_make_pdf("Some totally unrelated text"))
    pp = _passport_with_manufacturer(address=None, company="ACME")  # 4 chars

    verify_grounded_strings(pp, [p])
    assert pp.overview.manufacturer.company_name.value == "ACME"


def test_no_pdfs_is_noop(tmp_path):
    """Extraction from images/xlsx/URL only — no PDF corpus to verify against.
    Guard must NOT blank everything; that would be a regression."""
    pp = _passport_with_manufacturer(
        address="Via Emilia 42",
        company="Ediltech Srl",
    )
    xlsx = tmp_path / "bom.xlsx"
    xlsx.write_bytes(b"not a real xlsx, but a non-PDF path")

    stats = verify_grounded_strings(pp, [xlsx])

    assert pp.overview.manufacturer.address.value == "Via Emilia 42"
    assert pp.overview.manufacturer.company_name.value == "Ediltech Srl"
    assert stats["blanked"] == 0
    assert stats["corpus_chars"] == 0


def test_empty_passport_is_noop(tmp_path):
    pytest.importorskip("reportlab")
    p = tmp_path / "doc.pdf"
    p.write_bytes(_make_pdf("Some text"))
    from dpp_extractor.pipeline.merge import merge_extractions
    pp, _ = merge_extractions([], ProductFamily.OTH)
    stats = verify_grounded_strings(pp, [p])
    assert stats["blanked"] == 0
