"""Tests for M59 — Document Ingestion Pipeline.

Validates:
1. Document adapters (CSV, TXT)
2. Chunking engine
3. Duplicate detection
4. Document registry
5. Full ingestion pipeline (end-to-end)
6. Document type guessing
"""
from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixtures: Synthetic demo documents
# ---------------------------------------------------------------------------

SAMPLE_INSPECTION_TEXT = """
INSPECTION REPORT IR-104

Equipment: P-101 Centrifugal Cooling Water Pump
Location: Area A, Cooling Water System
Inspector: John Smith
Date: 2024-01-15

1. VISUAL INSPECTION
The pump housing and baseplate were inspected visually.
Minor surface corrosion was noted on the baseplate bolts.
No visible leaks from mechanical seal.

2. VIBRATION ANALYSIS
Drive-end bearing vibration reading: 8.5 mm/s (ALARM)
Non-drive-end bearing vibration reading: 3.2 mm/s (NORMAL)
Normal range: 0-7.0 mm/s per ISO 10816

3. TEMPERATURE READINGS
Drive-end bearing temperature: 82°C (ELEVATED)
Non-drive-end bearing temperature: 55°C (NORMAL)
Normal operating range: 40-70°C

4. FINDINGS
- High vibration on drive-end bearing exceeding alarm threshold
- Elevated temperature on drive-end bearing
- Vibration trend increasing over last 3 inspection cycles
- Pattern consistent with bearing degradation

5. RECOMMENDATIONS
- Replace drive-end bearing within 30 days
- Priority: URGENT
- Failure mode: Bearing degradation due to lubrication issues
- If deferred, risk of catastrophic bearing failure and pump seizure

6. NEXT INSPECTION
Scheduled: 2024-02-15 (30 days)
Type: Vibration monitoring
""".strip()


SAMPLE_MAINTENANCE_CSV = """work_order_id,equipment_tag,title,work_type,priority,status,performed_by,performed_date,labor_hours,cost
WO-281,P-101,Quarterly lubrication,preventive,normal,COMPLETED,Mike Johnson,2023-06-15,2.0,150
WO-285,P-101,Vibration check,predictive,normal,COMPLETED,John Smith,2023-09-10,1.5,100
WO-288,P-102,Seal replacement,corrective,urgent,COMPLETED,Sarah Davis,2023-10-22,8.0,2500
WO-291,P-101,Replace drive-end bearing,corrective,urgent,DEFERRED,,,0,0
WO-295,V-204,Valve inspection,preventive,normal,COMPLETED,Mike Johnson,2024-01-05,1.0,75
WO-298,P-101,Emergency bearing replacement,emergency,emergency,COMPLETED,John Smith,2024-04-18,12.0,4500
""".strip()


SAMPLE_INCIDENT_TEXT = """
INCIDENT REPORT IN-44

Equipment: P-101 Centrifugal Cooling Water Pump
Location: Area A, Cooling Water System
Date: 2024-04-15
Reported by: Shift Operator Tom Wilson
Severity: MAJOR

DESCRIPTION
At approximately 14:30, operators observed abnormal noise and smoke
from the drive-end bearing housing of Pump P-101. The pump was
immediately shut down per emergency procedure SOP-EM-001.

Investigation revealed that the drive-end bearing had seized
completely, causing scoring of the shaft journal and damage to
the bearing housing.

ROOT CAUSE
Bearing failure due to progressive lubrication degradation.
Contributing factors:
- Work Order WO-291 for bearing replacement was deferred in February 2024
- Inspection Report IR-104 (January 2024) identified high vibration
- Inspection Report IR-109 (March 2024) showed worsening trend
- Bearing was operating beyond recommended replacement interval

IMPACT
- Unplanned pump shutdown: 48 hours
- Production impact: Reduced cooling capacity
- Repair cost: $4,500 (emergency bearing replacement + shaft repair)
- No safety or environmental impact

CORRECTIVE ACTIONS
1. Emergency bearing replacement completed (WO-298)
2. Shaft journal polished and within tolerance
3. New vibration baseline established post-repair

PREVENTIVE ACTIONS
1. Review maintenance deferral approval process
2. Implement automatic escalation for deferred URGENT recommendations
3. Add P-101 to predictive maintenance monitoring program
""".strip()


# ---------------------------------------------------------------------------
# Tests: TXT Adapter
# ---------------------------------------------------------------------------

class TestTXTAdapter:
    def test_extract_text_file(self, tmp_path: Path):
        from app.ingestion.adapters.txt_adapter import TXTAdapter
        adapter = TXTAdapter()

        file_path = tmp_path / "Inspection_Report_IR104.txt"
        file_path.write_text(SAMPLE_INSPECTION_TEXT, encoding="utf-8")

        assert adapter.can_handle(file_path) is True
        result = adapter.extract(file_path)

        assert result.total_pages == 1
        assert len(result.pages) == 1
        assert "P-101" in result.pages[0].text
        assert "8.5 mm/s" in result.pages[0].text
        assert result.extraction_method == "text_extraction"

    def test_unsupported_extension(self, tmp_path: Path):
        from app.ingestion.adapters.txt_adapter import TXTAdapter
        adapter = TXTAdapter()
        assert adapter.can_handle(tmp_path / "file.pdf") is False


# ---------------------------------------------------------------------------
# Tests: CSV Adapter
# ---------------------------------------------------------------------------

class TestCSVAdapter:
    def test_extract_csv_file(self, tmp_path: Path):
        from app.ingestion.adapters.csv_adapter import CSVAdapter
        adapter = CSVAdapter()

        file_path = tmp_path / "Maintenance_History.csv"
        file_path.write_text(SAMPLE_MAINTENANCE_CSV, encoding="utf-8")

        assert adapter.can_handle(file_path) is True
        result = adapter.extract(file_path)

        assert result.total_pages == 1
        assert len(result.pages) == 1
        page = result.pages[0]
        assert page.tables is not None
        assert len(page.tables) == 1
        table = page.tables[0]
        assert len(table) == 7  # 1 header + 6 data rows
        assert "P-101" in page.text
        assert page.metadata["row_count"] == 6

    def test_empty_csv(self, tmp_path: Path):
        from app.ingestion.adapters.csv_adapter import CSVAdapter
        adapter = CSVAdapter()
        file_path = tmp_path / "empty.csv"
        file_path.write_text("", encoding="utf-8")
        result = adapter.extract(file_path)
        assert result.total_pages == 1


# ---------------------------------------------------------------------------
# Tests: Chunking Engine
# ---------------------------------------------------------------------------

class TestChunkingEngine:
    def test_chunk_short_text(self):
        from app.ingestion.adapters.base import ExtractedPage
        from app.ingestion.chunking.chunker import ChunkingEngine, ChunkingConfig

        config = ChunkingConfig(max_chunk_size=2000, chunk_overlap=0, min_chunk_size=100)
        engine = ChunkingEngine(config)

        pages = (ExtractedPage(page_number=1, text="Short text."),)
        chunks = engine.chunk_pages(pages, "DOC-001", "test.txt", "GENERAL")
        assert len(chunks) == 0  # Too short (< min_chunk_size of 100)

    def test_chunk_long_text(self):
        from app.ingestion.adapters.base import ExtractedPage
        from app.ingestion.chunking.chunker import ChunkingEngine, ChunkingConfig

        config = ChunkingConfig(max_chunk_size=500, chunk_overlap=0, min_chunk_size=10)
        engine = ChunkingEngine(config)

        pages = (ExtractedPage(page_number=1, text=SAMPLE_INSPECTION_TEXT),)
        chunks = engine.chunk_pages(pages, "DOC-001", "ir104.txt", "INSPECTION_REPORT")

        assert len(chunks) > 1
        # Every chunk has provenance
        for chunk in chunks:
            assert chunk.provenance is not None
            assert chunk.provenance.document_id == "DOC-001"
            assert chunk.provenance.document_name == "ir104.txt"
            assert chunk.chunk_id is not None

    def test_chunk_with_tables(self):
        from app.ingestion.adapters.base import ExtractedPage
        from app.ingestion.chunking.chunker import ChunkingEngine, ChunkingConfig

        config = ChunkingConfig(max_chunk_size=500, chunk_overlap=0, min_chunk_size=10)
        engine = ChunkingEngine(config)

        table = [
            ["Equipment", "Vibration", "Status"],
            ["P-101 DE", "8.5", "ALARM"],
            ["P-101 NDE", "3.2", "NORMAL"],
        ]
        pages = (ExtractedPage(
            page_number=1,
            text="Some text here.",
            tables=(table,),
        ),)
        chunks = engine.chunk_pages(pages, "DOC-001", "test.txt", "GENERAL")

        # Should have at least one table chunk
        table_chunks = [c for c in chunks if c.provenance and c.provenance.extraction_method == "table_parse"]
        assert len(table_chunks) >= 1

    def test_provenance_preservation(self):
        from app.ingestion.adapters.base import ExtractedPage
        from app.ingestion.chunking.chunker import ChunkingEngine, ChunkingConfig

        config = ChunkingConfig(max_chunk_size=200, chunk_overlap=0, min_chunk_size=10)
        engine = ChunkingEngine(config)

        pages = (ExtractedPage(page_number=3, text=SAMPLE_INSPECTION_TEXT),)
        chunks = engine.chunk_pages(pages, "DOC-003", "IR-104.pdf", "INSPECTION_REPORT")

        for chunk in chunks:
            assert chunk.provenance.document_id == "DOC-003"
            assert chunk.provenance.page_number == 3
            assert chunk.provenance.document_type == "INSPECTION_REPORT"


# ---------------------------------------------------------------------------
# Tests: Duplicate Detector
# ---------------------------------------------------------------------------

class TestDuplicateDetector:
    def test_no_duplicates(self, tmp_path: Path):
        from app.ingestion.duplicate_detector import DuplicateDetector
        detector = DuplicateDetector()

        f1 = tmp_path / "file1.txt"
        f1.write_text("content 1")
        hash1 = detector.compute_hash(f1)

        assert detector.is_duplicate(hash1) is False

    def test_detect_duplicate(self, tmp_path: Path):
        from app.ingestion.duplicate_detector import DuplicateDetector
        detector = DuplicateDetector()

        f1 = tmp_path / "file1.txt"
        f1.write_text("same content")
        hash1 = detector.compute_hash(f1)

        detector.register(hash1, "DOC-001")
        assert detector.is_duplicate(hash1) is True
        assert detector.get_existing_document_id(hash1) == "DOC-001"

    def test_different_files_different_hashes(self, tmp_path: Path):
        from app.ingestion.duplicate_detector import DuplicateDetector
        detector = DuplicateDetector()

        f1 = tmp_path / "file1.txt"
        f1.write_text("content A")
        f2 = tmp_path / "file2.txt"
        f2.write_text("content B")

        assert detector.compute_hash(f1) != detector.compute_hash(f2)


# ---------------------------------------------------------------------------
# Tests: Document Registry
# ---------------------------------------------------------------------------

class TestDocumentRegistry:
    def test_register_and_get(self):
        from app.ingestion.document_registry import DocumentRegistry
        from app.domain.industrial.document import Document, DocumentType, DocumentFormat

        registry = DocumentRegistry()
        doc = Document(
            document_id="DOC-001",
            name="test.pdf",
            document_type=DocumentType.INSPECTION_REPORT,
            document_format=DocumentFormat.PDF,
            file_hash="abc123",
        )
        registry.register(doc)
        assert registry.get("DOC-001") == doc
        assert registry.document_count == 1

    def test_find_by_type(self):
        from app.ingestion.document_registry import DocumentRegistry
        from app.domain.industrial.document import Document, DocumentType, DocumentFormat

        registry = DocumentRegistry()
        registry.register(Document(
            document_id="DOC-001", name="ir.pdf",
            document_type=DocumentType.INSPECTION_REPORT,
            document_format=DocumentFormat.PDF, file_hash="a",
        ))
        registry.register(Document(
            document_id="DOC-002", name="wo.pdf",
            document_type=DocumentType.MAINTENANCE_WORK_ORDER,
            document_format=DocumentFormat.PDF, file_hash="b",
        ))

        inspections = registry.find_by_type(DocumentType.INSPECTION_REPORT)
        assert len(inspections) == 1
        assert inspections[0].document_id == "DOC-001"


# ---------------------------------------------------------------------------
# Tests: Document Type Guessing
# ---------------------------------------------------------------------------

class TestDocumentTypeGuessing:
    def test_inspection_report(self):
        from app.ingestion.ingestion_pipeline import guess_document_type
        from app.domain.industrial.document import DocumentType

        assert guess_document_type(Path("Inspection_Report_IR104.pdf")) == DocumentType.INSPECTION_REPORT
        assert guess_document_type(Path("IR-104.pdf")) == DocumentType.INSPECTION_REPORT

    def test_work_order(self):
        from app.ingestion.ingestion_pipeline import guess_document_type
        from app.domain.industrial.document import DocumentType

        assert guess_document_type(Path("Work_Order_WO291.pdf")) == DocumentType.MAINTENANCE_WORK_ORDER
        assert guess_document_type(Path("WO-291.pdf")) == DocumentType.MAINTENANCE_WORK_ORDER

    def test_incident(self):
        from app.ingestion.ingestion_pipeline import guess_document_type
        from app.domain.industrial.document import DocumentType

        assert guess_document_type(Path("Incident_Report_IN44.pdf")) == DocumentType.INCIDENT_REPORT

    def test_oem_manual(self):
        from app.ingestion.ingestion_pipeline import guess_document_type
        from app.domain.industrial.document import DocumentType

        assert guess_document_type(Path("OEM_Manual_P101.pdf")) == DocumentType.OEM_MANUAL

    def test_csv_default(self):
        from app.ingestion.ingestion_pipeline import guess_document_type
        from app.domain.industrial.document import DocumentType

        assert guess_document_type(Path("data.csv")) == DocumentType.MAINTENANCE_HISTORY

    def test_general_fallback(self):
        from app.ingestion.ingestion_pipeline import guess_document_type
        from app.domain.industrial.document import DocumentType

        assert guess_document_type(Path("random_document.pdf")) == DocumentType.GENERAL


# ---------------------------------------------------------------------------
# Tests: Full Ingestion Pipeline (end-to-end)
# ---------------------------------------------------------------------------

class TestIngestionPipeline:
    def test_ingest_txt_file(self, tmp_path: Path):
        from app.ingestion.ingestion_pipeline import IngestionPipeline

        file_path = tmp_path / "Inspection_Report_IR104.txt"
        file_path.write_text(SAMPLE_INSPECTION_TEXT, encoding="utf-8")

        pipeline = IngestionPipeline()
        result = pipeline.ingest(file_path)

        assert result.status == "PROCESSED"
        assert result.chunk_count > 0
        assert result.page_count == 1
        assert result.document_name == "Inspection_Report_IR104.txt"
        assert result.metadata["document_type"] == "INSPECTION_REPORT"

        # Verify document is registered
        doc = pipeline.registry.get(result.document_id)
        assert doc is not None
        assert doc.document_id == result.document_id

    def test_ingest_csv_file(self, tmp_path: Path):
        from app.ingestion.ingestion_pipeline import IngestionPipeline

        file_path = tmp_path / "Maintenance_History.csv"
        file_path.write_text(SAMPLE_MAINTENANCE_CSV, encoding="utf-8")

        pipeline = IngestionPipeline()
        result = pipeline.ingest(file_path)

        assert result.status == "PROCESSED"
        assert result.chunk_count > 0
        assert result.metadata["document_type"] == "MAINTENANCE_HISTORY"

    def test_duplicate_detection(self, tmp_path: Path):
        from app.ingestion.ingestion_pipeline import IngestionPipeline

        file_path = tmp_path / "test.txt"
        file_path.write_text(SAMPLE_INSPECTION_TEXT, encoding="utf-8")

        pipeline = IngestionPipeline()

        # First ingestion
        result1 = pipeline.ingest(file_path)
        assert result1.status == "PROCESSED"

        # Second ingestion — should be duplicate
        result2 = pipeline.ingest(file_path)
        assert result2.status == "DUPLICATE"
        assert result2.duplicate_of == result1.document_id

    def test_ingest_nonexistent_file(self, tmp_path: Path):
        from app.ingestion.ingestion_pipeline import IngestionPipeline

        pipeline = IngestionPipeline()
        result = pipeline.ingest(tmp_path / "nonexistent.pdf")
        assert result.status == "ERROR"
        assert len(result.errors) > 0

    def test_ingest_unsupported_format(self, tmp_path: Path):
        from app.ingestion.ingestion_pipeline import IngestionPipeline

        file_path = tmp_path / "file.xyz"
        file_path.write_text("content")

        pipeline = IngestionPipeline()
        result = pipeline.ingest(file_path)
        assert result.status == "ERROR"

    def test_ingest_directory(self, tmp_path: Path):
        from app.ingestion.ingestion_pipeline import IngestionPipeline

        # Create multiple files
        (tmp_path / "Inspection_Report_IR104.txt").write_text(SAMPLE_INSPECTION_TEXT)
        (tmp_path / "Incident_Report_IN44.txt").write_text(SAMPLE_INCIDENT_TEXT)
        (tmp_path / "Maintenance_History.csv").write_text(SAMPLE_MAINTENANCE_CSV)

        pipeline = IngestionPipeline()
        results = pipeline.ingest_directory(tmp_path)

        assert len(results) == 3
        assert all(r.status == "PROCESSED" for r in results)
        assert pipeline.registry.document_count == 3
        assert pipeline.registry.total_chunk_count > 0

    def test_chunks_have_provenance(self, tmp_path: Path):
        from app.ingestion.ingestion_pipeline import IngestionPipeline

        file_path = tmp_path / "Inspection_Report_IR104.txt"
        file_path.write_text(SAMPLE_INSPECTION_TEXT, encoding="utf-8")

        pipeline = IngestionPipeline()
        result = pipeline.ingest(file_path)

        chunks = pipeline.registry.get_chunks(result.document_id)
        for chunk in chunks:
            assert chunk.provenance is not None
            assert chunk.provenance.document_id == result.document_id
            assert chunk.provenance.document_name == "Inspection_Report_IR104.txt"
            assert chunk.provenance.document_type == "INSPECTION_REPORT"

    def test_full_demo_scenario(self, tmp_path: Path):
        """Simulate the hackathon demo: ingest 3 documents for the P-101 story."""
        from app.ingestion.ingestion_pipeline import IngestionPipeline
        from app.domain.industrial.document import DocumentType

        # Create demo documents
        (tmp_path / "Inspection_Report_IR104.txt").write_text(SAMPLE_INSPECTION_TEXT)
        (tmp_path / "Maintenance_History.csv").write_text(SAMPLE_MAINTENANCE_CSV)
        (tmp_path / "Incident_Report_IN44.txt").write_text(SAMPLE_INCIDENT_TEXT)

        pipeline = IngestionPipeline()
        results = pipeline.ingest_directory(tmp_path)

        # All processed
        assert len(results) == 3
        assert all(r.status == "PROCESSED" for r in results)

        # Correct type guessing
        types = {r.metadata.get("document_type") for r in results}
        assert "INSPECTION_REPORT" in types
        assert "MAINTENANCE_HISTORY" in types
        assert "INCIDENT_REPORT" in types

        # All chunks searchable
        all_chunks = pipeline.registry.get_all_chunks()
        assert len(all_chunks) > 5  # Should have many chunks

        # P-101 appears in multiple chunks
        p101_chunks = [c for c in all_chunks if "P-101" in c.content]
        assert len(p101_chunks) >= 2  # At least inspection + incident mention P-101
