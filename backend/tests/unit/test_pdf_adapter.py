import pytest
from pathlib import Path
from app.ingestion.adapters.pdf_adapter import PDFAdapter
from app.ingestion.adapters.base import ExtractionResult
from pypdf import PdfWriter

@pytest.fixture
def temp_pdfs(tmp_path):
    # Empty PDF
    empty_pdf_path = tmp_path / "empty.pdf"
    writer_empty = PdfWriter()
    writer_empty.add_blank_page(width=200, height=200)
    with open(empty_pdf_path, "wb") as f:
        writer_empty.write(f)

    # Corrupted PDF
    corrupt_pdf_path = tmp_path / "corrupt.pdf"
    corrupt_pdf_path.write_text("not a pdf")

    return {
        "empty": empty_pdf_path,
        "corrupt": corrupt_pdf_path,
    }

def test_pdf_adapter_empty_or_scanned(temp_pdfs):
    adapter = PDFAdapter()
    result = adapter.extract(temp_pdfs["empty"])
    assert result.total_pages == 1
    assert result.extraction_method == "pypdf"
    
    # We expect an error about OCR not being supported for image-only/empty pages
    error_str = " ".join(result.errors)
    assert "OCR not supported" in error_str

def test_pdf_adapter_corrupt(temp_pdfs):
    adapter = PDFAdapter()
    result = adapter.extract(temp_pdfs["corrupt"])
    assert result.total_pages == 0
    assert result.extraction_method == "failed"
    
    error_str = " ".join(result.errors)
    assert "Failed to extract text from PDF corrupt.pdf" in error_str
