"""
Pass 1 — Document Classification.

Takes a PDF and classifies it by document type and product family.
Uses pydantic_ai Agent with Gemini via Google Vertex AI.
"""

import logging
from pathlib import Path

from pydantic_ai import Agent, BinaryContent

from ..models.classification import DocumentClassification
from ..prompts.classification import CLASSIFICATION_SYSTEM_PROMPT
from .model_factory import create_gemini_model

logger = logging.getLogger(__name__)

# Media type mapping
MEDIA_TYPES: dict[str, str] = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
}


def _get_media_type(path: Path) -> str:
    ext = path.suffix.lower()
    media = MEDIA_TYPES.get(ext)
    if not media:
        raise ValueError(f"Unsupported file type: {ext}")
    return media


class ClassificationAgent:
    """Pass 1 agent — classifies a single document."""

    def __init__(self) -> None:
        self.agent = Agent(
            create_gemini_model(),
            output_type=DocumentClassification,
            system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
            model_settings={"temperature": 0.0},
        )
        logger.info("ClassificationAgent initialized")

    async def classify(self, file_path: Path) -> DocumentClassification:
        """
        Classify a single document.

        Args:
            file_path: Path to the PDF/image file.

        Returns:
            DocumentClassification with type, family, and metadata.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        logger.info(f"Classifying: {file_path.name} ({file_size_mb:.1f} MB)")

        media_type = _get_media_type(file_path)
        file_data = file_path.read_bytes()
        binary = BinaryContent(data=file_data, media_type=media_type)

        result = await self.agent.run([
            f"Classify this construction-product document: {file_path.name}",
            binary,
        ])

        classification = result.output
        logger.info(
            f"Classified {file_path.name}: "
            f"type={classification.document_type.value} "
            f"(conf={classification.document_type_confidence:.2f}), "
            f"family={classification.product_family.value if classification.product_family else 'unknown'}"
        )
        return classification
