"""Document Ingestion Pipeline.

Orchestrates the complete document ingestion workflow:
1. File detection → adapter routing
2. Content extraction (text + tables)
3. Duplicate detection
4. Semantic chunking
5. Document registration
6. Observation generation

This is the single entry point for all document ingestion.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.domain.industrial.document import (
    Document,
    DocumentChunk,
    DocumentFormat,
    DocumentMetadata,
    DocumentStatus,
    DocumentType,
)
from app.ingestion.adapters.base import DocumentAdapter, ExtractionResult
from app.ingestion.adapters.csv_adapter import CSVAdapter
from app.ingestion.adapters.pdf_adapter import PDFAdapter
from app.ingestion.adapters.txt_adapter import TXTAdapter
from app.ingestion.adapters.xlsx_adapter import XLSXAdapter
from app.ingestion.chunking.chunker import ChunkingConfig, ChunkingEngine
from app.ingestion.document_registry import DocumentRegistry
from app.ingestion.duplicate_detector import DuplicateDetector

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------

_EXTENSION_TO_FORMAT: dict[str, DocumentFormat] = {
    ".pdf": DocumentFormat.PDF,
    ".csv": DocumentFormat.CSV,
    ".xlsx": DocumentFormat.XLSX,
    ".xls": DocumentFormat.XLSX,
    ".txt": DocumentFormat.TXT,
    ".md": DocumentFormat.TXT,
    ".text": DocumentFormat.TXT,
    ".log": DocumentFormat.TXT,
    ".docx": DocumentFormat.DOCX,
    ".json": DocumentFormat.JSON,
}

_EXTENSION_TO_DOC_TYPE: dict[str, DocumentType] = {
    ".csv": DocumentType.MAINTENANCE_HISTORY,
    ".xlsx": DocumentType.SPREADSHEET,
    ".xls": DocumentType.SPREADSHEET,
}


def detect_format(file_path: Path) -> DocumentFormat:
    """Detect document format from file extension."""
    return _EXTENSION_TO_FORMAT.get(
        file_path.suffix.lower(),
        DocumentFormat.UNKNOWN,
    )


def guess_document_type(file_path: Path) -> DocumentType:
    """Guess document type from filename patterns.

    This is a heuristic — the actual type can be overridden
    by the user or by LLM classification.
    """
    name_lower = file_path.stem.lower()

    # Check filename patterns
    patterns = {
        "inspection": DocumentType.INSPECTION_REPORT,
        "ir-": DocumentType.INSPECTION_REPORT,
        "ir_": DocumentType.INSPECTION_REPORT,
        "work_order": DocumentType.MAINTENANCE_WORK_ORDER,
        "wo-": DocumentType.MAINTENANCE_WORK_ORDER,
        "wo_": DocumentType.MAINTENANCE_WORK_ORDER,
        "incident": DocumentType.INCIDENT_REPORT,
        "in-": DocumentType.INCIDENT_REPORT,
        "oem": DocumentType.OEM_MANUAL,
        "manual": DocumentType.OEM_MANUAL,
        "sop": DocumentType.SOP,
        "procedure": DocumentType.PROCEDURE,
        "regulation": DocumentType.REGULATION,
        "standard": DocumentType.REGULATION,
        "maintenance_history": DocumentType.MAINTENANCE_HISTORY,
        "near_miss": DocumentType.NEAR_MISS_REPORT,
        "audit": DocumentType.AUDIT_FINDING,
        "datasheet": DocumentType.DATASHEET,
        "specification": DocumentType.SPECIFICATION,
    }

    for pattern, doc_type in patterns.items():
        if pattern in name_lower:
            return doc_type

    # Fall back to extension-based guess
    return _EXTENSION_TO_DOC_TYPE.get(
        file_path.suffix.lower(),
        DocumentType.GENERAL,
    )


# ---------------------------------------------------------------------------
# Ingestion Result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IngestionResult:
    """Result of ingesting a single document."""
    document_id: str
    document_name: str
    status: str
    chunk_count: int = 0
    page_count: int = 0
    errors: tuple[str, ...] = ()
    duplicate_of: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Ingestion Pipeline
# ---------------------------------------------------------------------------


class IngestionPipeline:
    """Orchestrates the complete document ingestion workflow.

    Usage:
        pipeline = IngestionPipeline()
        result = pipeline.ingest(Path("document.pdf"))
        results = pipeline.ingest_directory(Path("documents/"))
    """

    def __init__(
        self,
        registry: DocumentRegistry | None = None,
        chunking_config: ChunkingConfig | None = None,
    ) -> None:
        self._registry = registry or DocumentRegistry()
        self._duplicate_detector = DuplicateDetector()
        self._chunker = ChunkingEngine(chunking_config)

        # Register all adapters
        self._adapters: list[DocumentAdapter] = [
            PDFAdapter(),
            CSVAdapter(),
            XLSXAdapter(),
            TXTAdapter(),
        ]

    @property
    def registry(self) -> DocumentRegistry:
        return self._registry

    def ingest(
        self,
        file_path: Path,
        document_type: DocumentType | None = None,
    ) -> IngestionResult:
        """Ingest a single document.

        Steps:
        1. Validate file exists
        2. Compute file hash for duplicate detection
        3. Select appropriate adapter
        4. Extract content (text + tables)
        5. Chunk content with provenance
        6. Register document and chunks
        """
        file_path = Path(file_path)

        # 1. Validate
        if not file_path.exists():
            return IngestionResult(
                document_id="",
                document_name=file_path.name,
                status="ERROR",
                errors=(f"File not found: {file_path}",),
            )

        # 2. Duplicate detection
        file_hash = self._duplicate_detector.compute_hash(file_path)
        if self._duplicate_detector.is_duplicate(file_hash):
            existing_id = self._duplicate_detector.get_existing_document_id(file_hash)
            return IngestionResult(
                document_id=existing_id or "",
                document_name=file_path.name,
                status="DUPLICATE",
                duplicate_of=existing_id,
            )

        # 3. Select adapter
        adapter = self._select_adapter(file_path)
        if adapter is None:
            return IngestionResult(
                document_id="",
                document_name=file_path.name,
                status="ERROR",
                errors=(f"No adapter for file type: {file_path.suffix}",),
            )

        # 4. Extract content
        extraction = adapter.extract(file_path)
        if not extraction.pages and extraction.errors:
            return IngestionResult(
                document_id="",
                document_name=file_path.name,
                status="ERROR",
                errors=extraction.errors,
            )

        # 5. Create document
        document_id = f"DOC-{uuid4().hex[:8].upper()}"
        doc_format = detect_format(file_path)
        doc_type = document_type or guess_document_type(file_path)

        doc_metadata = DocumentMetadata(
            page_count=extraction.total_pages,
            word_count=sum(len(p.text.split()) for p in extraction.pages),
        )

        # 6. Chunk content
        chunks = self._chunker.chunk_pages(
            pages=extraction.pages,
            document_id=document_id,
            document_name=file_path.name,
            document_type=doc_type.value,
        )

        # 7. Register document
        document = Document(
            document_id=document_id,
            name=file_path.name,
            document_type=doc_type,
            document_format=doc_format,
            file_hash=file_hash,
            file_path=str(file_path),
            file_size_bytes=file_path.stat().st_size,
            status=DocumentStatus.PROCESSED,
            ingested_at=datetime.now(),
            doc_metadata=doc_metadata,
            chunks=tuple(chunks),
        )

        self._registry.register(document)
        self._registry.store_chunks(document_id, chunks)
        self._duplicate_detector.register(file_hash, document_id)

        logger.info(
            f"Ingested {file_path.name}: {len(chunks)} chunks, "
            f"{extraction.total_pages} pages, type={doc_type.value}"
        )

        return IngestionResult(
            document_id=document_id,
            document_name=file_path.name,
            status="PROCESSED",
            chunk_count=len(chunks),
            page_count=extraction.total_pages,
            errors=extraction.errors,
            metadata={
                "document_type": doc_type.value,
                "format": doc_format.value,
                "extraction_method": extraction.extraction_method,
            },
        )

    def ingest_directory(
        self,
        directory: Path,
        recursive: bool = False,
    ) -> list[IngestionResult]:
        """Ingest all supported documents in a directory."""
        results: list[IngestionResult] = []
        directory = Path(directory)

        if not directory.exists() or not directory.is_dir():
            return results

        # Collect supported file extensions
        supported = set()
        for adapter in self._adapters:
            supported.update(adapter.supported_extensions)

        # Find files
        pattern = "**/*" if recursive else "*"
        for file_path in sorted(directory.glob(pattern)):
            if file_path.is_file() and file_path.suffix.lower() in supported:
                result = self.ingest(file_path)
                results.append(result)

        return results

    def _select_adapter(self, file_path: Path) -> DocumentAdapter | None:
        """Select the appropriate adapter for a file."""
        for adapter in self._adapters:
            if adapter.can_handle(file_path):
                return adapter
        return None
