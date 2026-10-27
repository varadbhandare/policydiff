import pytest
import io
from pathlib import Path
from app.services.document_extractor import (
    DocumentExtractor,
    DocumentExtractionError,
    ScannedPdfError,
)
from app.services.demo_generator import generate_sample_files


def test_txt_extraction():
    content = "Section 1: Academic Attendance\nStudents must attend at least 75% of classes."
    doc = DocumentExtractor.extract_from_bytes(content.encode("utf-8"), "test_policy.txt")
    assert doc.file_type == "txt"
    assert "75%" in doc.full_text
    assert len(doc.pages) == 1


def test_pdf_extraction():
    paths = generate_sample_files()
    pdf_bytes = Path(paths["old_pdf"]).read_bytes()
    doc = DocumentExtractor.extract_from_bytes(pdf_bytes, "Apex_University_Academic_Policy_2025.pdf")
    assert doc.file_type == "pdf"
    assert "Apex University" in doc.full_text
    assert "75%" in doc.full_text
    assert doc.total_characters > 100


def test_docx_extraction():
    paths = generate_sample_files()
    docx_bytes = Path(paths["old_docx"]).read_bytes()
    doc = DocumentExtractor.extract_from_bytes(docx_bytes, "Apex_University_Academic_Policy_2025.docx")
    assert doc.file_type == "docx"
    assert "Apex University" in doc.full_text
    assert "75%" in doc.full_text


def test_unsupported_file_extension():
    with pytest.raises(DocumentExtractionError) as exc_info:
        DocumentExtractor.extract_from_bytes(b"some content", "policy.xlsx")
    assert "Unsupported file format" in str(exc_info.value)


def test_scanned_or_empty_pdf_detection():
    # Create a 1-page PDF with no text (empty canvas)
    import pymupdf as fitz
    empty_doc = fitz.open()
    empty_doc.new_page()
    pdf_bytes = empty_doc.tobytes()
    empty_doc.close()

    with pytest.raises(ScannedPdfError) as exc_info:
        DocumentExtractor.extract_from_bytes(pdf_bytes, "scanned_document.pdf")
    assert "Scanned PDF detected" in str(exc_info.value)
