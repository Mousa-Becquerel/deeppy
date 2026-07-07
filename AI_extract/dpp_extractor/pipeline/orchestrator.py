"""
Pipeline orchestrator — ties together Pass 1, 2, and 3.

Usage:
    orchestrator = PipelineOrchestrator()
    passport, merge_result = await orchestrator.process(file_paths)
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Optional, Callable
from collections import Counter

from ..config import MAX_CONCURRENT_EXTRACTIONS
from ..models.classification import DocumentClassification
from ..models.extraction_output import DocumentExtractionOutput
from ..models.passport import DigitalProductPassport
from ..models.merge_result import MergeResult
from ..ontology.enums import ProductFamily
from .classify import ClassificationAgent
from .extract import ExtractionAgent
from .merge import merge_extractions
from .postprocess import (
    populate_compliance_presence,
    populate_documents_section,
    simplify_multi_variant_product_name,
)

logger = logging.getLogger(__name__)

# Retry settings for 429 rate limiting
MAX_RETRIES = 3
RETRY_BASE_DELAY = 5  # seconds


class PipelineOrchestrator:
    """
    Three-pass pipeline: classify → extract → merge.

    Processes a set of PDF documents for a single product and produces
    a complete DigitalProductPassport.
    """

    def __init__(self) -> None:
        self._classifier = ClassificationAgent()
        self._extractor = ExtractionAgent()
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENT_EXTRACTIONS)

    async def process(
        self,
        file_paths: list[Path],
        product_family_override: Optional[ProductFamily] = None,
        on_progress: Optional[Callable] = None,
        website_url: Optional[str] = None,
        bom_data_list: Optional[list[dict]] = None,
    ) -> tuple[DigitalProductPassport, MergeResult]:
        """
        Run the full 3-pass pipeline on a set of documents.

        Args:
            file_paths: Paths to PDF/image files for one product.
            product_family_override: Skip family detection, use this family.
            on_progress: Optional callback(step, doc_index, doc_total, detail).
            website_url: Optional product webpage URL to fetch additional data from.

        Returns:
            (DigitalProductPassport, MergeResult) tuple.
        """
        start = time.time()
        n = len(file_paths)
        logger.info(f"Pipeline starting: {n} documents" + (f", website: {website_url}" if website_url else ""))
        _report = on_progress or (lambda **kw: None)

        classifications = []
        family = product_family_override or ProductFamily.OTH

        if file_paths:
            # ── Pass 1: Classify all documents ──
            logger.info("=== Pass 1: Classification ===")
            classifications = await self._classify_all(file_paths, _report)

            # Determine consensus product family
            family = product_family_override or self._consensus_family(classifications)
            logger.info(f"Consensus product family: {family.value}")

            # Backfill failed classifications with fallback using consensus family
            classifications = self._backfill_classifications(classifications, file_paths, family)

        # ── Pass 2: Extract from each document (+ optional website) ──
        logger.info("=== Pass 2: Extraction ===")
        extractions = []

        if file_paths:
            extractions = await self._extract_all(
                file_paths, classifications, _report,
                website_url=website_url,
                bom_data_list=bom_data_list,
                consensus_family=family,
            )
        elif website_url or bom_data_list:
            # No PDFs — extract from URL/BoM-only context
            label = website_url or "BoM-only"
            logger.info(f"Document-less extraction (context only): {label}")
            _report(step="extract", doc_index=1, doc_total=1, detail=label)
            from ..ontology.enums import DocumentType
            fallback_cls = DocumentClassification(
                document_type=DocumentType.OTHER,
                document_type_confidence=0.0,
                product_family=family if family != ProductFamily.OTH else None,
                reason="No PDF documents provided; using website/BoM context only.",
            )
            result = await self._with_retry(
                self._extractor.extract,
                Path("/dev/null"),
                fallback_cls,
                website_url,
                bom_data_list,
                family,
                label=f"extract {label}",
            )
            if result:
                extractions.append(result)
                classifications.append(fallback_cls)
                file_paths = [Path(label)]  # use URL/BoM as "filename" for merge

        # ── Pass 3: Merge across documents ──
        logger.info("=== Pass 3: Merge ===")
        _report(step="merge", doc_index=0, doc_total=n, detail="Merging extracted data")
        extraction_triples = [
            (ext, cls, path.name)
            for path, cls, ext in zip(file_paths, classifications, extractions)
            if ext is not None
        ]

        # Fail loudly when every document failed to extract — otherwise the
        # job silently "succeeds" with an empty passport and the user has no
        # signal that anything went wrong (the common cause is a 403/quota on
        # the model API; we want that surfaced, not buried).
        had_inputs = bool(n or website_url or bom_data_list)
        if had_inputs and not extraction_triples:
            raise RuntimeError(
                f"All {n} document(s) failed to classify and extract. "
                "Check server logs for the underlying error — typical causes "
                "are an invalid/expired API key, rate-limit exhaustion, or "
                "unreadable PDFs."
            )

        passport, merge_result = merge_extractions(extraction_triples, family)

        # ── Post-processing: ontology-driven deterministic fills ──
        # 1. DoP/DoC/CE/Quality presence from classifications (no AI)
        # 2. Auto-link uploaded files to Documents section (no AI)
        # 3. Collapse multi-variant product_name to a single SKU when a BoM
        #    or filename pins down the target product.
        all_filenames = [p.name for p in file_paths]
        populate_compliance_presence(passport, classifications, all_filenames)
        populate_documents_section(passport, classifications, all_filenames)
        simplify_multi_variant_product_name(passport, bom_data_list, all_filenames)

        elapsed = time.time() - start
        logger.info(
            f"Pipeline complete in {elapsed:.1f}s: "
            f"{merge_result.total_fields_filled}/{merge_result.total_fields} fields filled, "
            f"{len(merge_result.conflicts)} conflicts"
        )

        return passport, merge_result

    async def _classify_all(
        self, file_paths: list[Path], report: Callable,
    ) -> list[Optional[DocumentClassification]]:
        """Classify documents with retry on any error."""
        n = len(file_paths)
        results = []
        for i, path in enumerate(file_paths):
            report(step="classify", doc_index=i + 1, doc_total=n, detail=path.name)
            result = await self._with_retry(
                self._classifier.classify, path,
                label=f"classify {path.name}",
            )
            results.append(result)
        return results

    def _backfill_classifications(
        self,
        classifications: list[Optional[DocumentClassification]],
        file_paths: list[Path],
        consensus_family: ProductFamily,
    ) -> list[DocumentClassification]:
        """Replace None classifications with a fallback using consensus family."""
        from ..ontology.enums import DocumentType
        backfilled = []
        for cls, path in zip(classifications, file_paths):
            if cls is not None:
                backfilled.append(cls)
            else:
                logger.warning(
                    f"Classification failed for {path.name} — "
                    f"using fallback (Other + {consensus_family.name})"
                )
                backfilled.append(DocumentClassification(
                    document_type=DocumentType.OTHER,
                    document_type_confidence=0.0,
                    product_family=consensus_family,
                    product_family_name=consensus_family.value,
                    product_name=None,
                    manufacturer=None,
                    language=None,
                    reference_standard=None,
                    reason=f"Classification failed (network error). Using consensus family {consensus_family.name} as fallback.",
                ))
        return backfilled

    async def _extract_all(
        self,
        file_paths: list[Path],
        classifications: list[DocumentClassification],
        report: Callable,
        website_url: Optional[str] = None,
        bom_data_list: Optional[list[dict]] = None,
        consensus_family: Optional[ProductFamily] = None,
    ) -> list[Optional[DocumentExtractionOutput]]:
        """Extract from documents sequentially with retry to avoid rate limits.

        Extraction order is sorted by document priority (DoP/Cert/TechSheet/EPD
        first, Catalog/Brochure last). This way catalogs can receive a
        "target product hint" derived from the already-extracted authoritative
        documents, which helps them ignore performance values for unrelated
        product variants documented in the same brochure.
        """
        from ..models.classification import DocumentType

        n = len(file_paths)

        # Priority order — lower number = extracted first
        DOC_PRIORITY = {
            DocumentType.DOP: 0,
            DocumentType.CERTIFICATE: 1,
            DocumentType.TECHNICAL_SHEET: 2,
            DocumentType.EPD: 3,
            DocumentType.SDS: 4,
            DocumentType.CATALOG: 5,
        }

        def _priority(cls) -> int:
            return DOC_PRIORITY.get(cls.document_type, 9) if cls else 9

        order = sorted(range(n), key=lambda i: _priority(classifications[i]))

        # Pick the BoM target: prefer the EPD (composition lives there), fall back
        # to the first doc with composition-bearing type, else index 0.
        bom_target_idx = 0
        if bom_data_list:
            composition_types = (DocumentType.EPD, DocumentType.DOP, DocumentType.TECHNICAL_SHEET)
            for ct in composition_types:
                for j, cls in enumerate(classifications):
                    if cls and cls.document_type == ct:
                        bom_target_idx = j
                        break
                else:
                    continue
                break
            logger.info(
                f"BoM will be injected into doc #{bom_target_idx + 1}: "
                f"{file_paths[bom_target_idx].name} "
                f"(type={classifications[bom_target_idx].document_type.value if classifications[bom_target_idx] else '?'})"
            )

        # Website URL goes to the highest-priority doc (first in extraction order)
        website_target_idx = order[0] if order else 0

        # Initialize result slots and rolling target hint
        results: list[Optional[DocumentExtractionOutput]] = [None] * n
        target_hint: dict[str, Optional[str]] = {"product_name": None, "uid": None, "dimension": None}

        for step_i, i in enumerate(order):
            path, cls = file_paths[i], classifications[i]
            report(step="extract", doc_index=step_i + 1, doc_total=n, detail=path.name)
            url = website_url if i == website_target_idx else None
            boms = bom_data_list if i == bom_target_idx else None

            # Provide target hint to catalogs/brochures so they filter cross-product noise
            hint = None
            if cls and cls.document_type == DocumentType.CATALOG and any(target_hint.values()):
                hint = dict(target_hint)

            result = await self._with_retry(
                self._extractor.extract, path, cls, url, boms, consensus_family, hint,
                label=f"extract {path.name}",
            )
            results[i] = result

            # Update target hint from authoritative docs (DoP/Cert/TechSheet)
            if result and cls and cls.document_type in (
                DocumentType.DOP, DocumentType.CERTIFICATE, DocumentType.TECHNICAL_SHEET
            ):
                self._update_target_hint(target_hint, result)

        return results

    @staticmethod
    def _update_target_hint(hint: dict, result) -> None:
        """Pull product_name / uid / dimension from a fresh extraction into the hint."""
        try:
            pi = result.passport.overview.product_info
            for key, source in (
                ("product_name", pi.product_name),
                ("uid", pi.uid),
                ("dimension", pi.standard_dimension),
            ):
                val = getattr(source, "value", None) if source else None
                if val and not hint.get(key):
                    hint[key] = val
        except AttributeError:
            pass

    async def _with_retry(self, fn, *args, label: str = ""):
        """Call fn with exponential backoff retry on any transient error."""
        for attempt in range(MAX_RETRIES + 1):
            try:
                return await fn(*args)
            except Exception as e:
                error_str = str(e)
                error_type = type(e).__name__
                is_retryable = (
                    "429" in error_str
                    or "RESOURCE_EXHAUSTED" in error_str
                    or "SSL" in error_str
                    or "ConnectionError" in error_str
                    or "timeout" in error_str.lower()
                    or "EOF" in error_str
                    # Network disconnect / protocol errors during long requests
                    or "disconnect" in error_str.lower()
                    or "Server disconnected" in error_str
                    or "RemoteProtocolError" in error_type
                    or "ReadError" in error_type
                    or "ReadTimeout" in error_type
                    or "WriteError" in error_type
                    or "ConnectError" in error_type
                    # Gemini 5xx errors (transient server issues)
                    or "500" in error_str
                    or "502" in error_str
                    or "503" in error_str
                    or "504" in error_str
                    or "INTERNAL" in error_str
                    or "UNAVAILABLE" in error_str
                    or "DEADLINE_EXCEEDED" in error_str
                )

                if is_retryable and attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(
                        f"Transient error on {label} (attempt {attempt + 1}/{MAX_RETRIES + 1}): "
                        f"{error_type}: {error_str[:120]}. Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Failed {label}: {error_type}: {error_str[:200]}")
                    return None

    def _consensus_family(
        self, classifications: list[DocumentClassification],
    ) -> ProductFamily:
        """Pick the most common product family across all classifications."""
        families = [
            c.product_family for c in classifications
            if c is not None and c.product_family is not None
        ]
        if not families:
            logger.warning("No product family detected in any document, using OTH")
            return ProductFamily.OTH

        counter = Counter(families)
        winner, count = counter.most_common(1)[0]
        logger.info(f"Family consensus: {winner.value} ({count}/{len(classifications)} docs)")
        return winner
