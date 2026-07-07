"""
CLI entry point for the DPP extraction pipeline.

Usage:
    python -m dpp_extractor /path/to/documents/folder
    python -m dpp_extractor file1.pdf file2.pdf file3.pdf
    python -m dpp_extractor /path/to/folder --output result.json
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from .config import OUTPUT_DIR
from .pipeline.orchestrator import PipelineOrchestrator


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("dpp_extractor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".tif"}


def collect_files(paths: list[str]) -> list[Path]:
    """Collect all supported files from given paths (files or directories)."""
    files = []
    for p in paths:
        path = Path(p)
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)
        elif path.is_dir():
            for ext in SUPPORTED_EXTENSIONS:
                files.extend(sorted(path.glob(f"*{ext}")))
        else:
            logger.warning(f"Skipping unsupported path: {path}")
    return files


async def run(args: argparse.Namespace) -> None:
    files = collect_files(args.inputs)
    if not files:
        logger.error("No supported files found.")
        sys.exit(1)

    logger.info(f"Found {len(files)} documents to process")
    for f in files:
        logger.info(f"  - {f.name}")

    orchestrator = PipelineOrchestrator()
    passport, merge_result = await orchestrator.process(files)

    # Write output
    output_path = Path(args.output) if args.output else OUTPUT_DIR / "passport.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = {
        "passport": passport.model_dump(mode="json"),
        "merge_result": merge_result.model_dump(mode="json"),
    }
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Output written to: {output_path}")

    # Summary
    print(f"\n{'='*60}")
    print(f"  DPP Extraction Complete")
    print(f"{'='*60}")
    print(f"  Documents processed:  {len(merge_result.documents_merged)}")
    print(f"  Fields filled:        {merge_result.total_fields_filled}/{merge_result.total_fields}")
    print(f"  Completeness:         {merge_result.completeness_pct:.1f}%")
    print(f"  Conflicts resolved:   {len(merge_result.conflicts)}")
    print(f"  Confidence: HIGH={merge_result.confidence_distribution.get('high', 0)}"
          f" MEDIUM={merge_result.confidence_distribution.get('medium', 0)}"
          f" LOW={merge_result.confidence_distribution.get('low', 0)}")
    print(f"  Output:               {output_path}")
    print(f"{'='*60}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DPP Extractor — Extract Digital Product Passport data from technical documents",
    )
    parser.add_argument(
        "inputs", nargs="+",
        help="PDF/image files or directories containing them",
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output JSON file path (default: output/passport.json)",
    )
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
