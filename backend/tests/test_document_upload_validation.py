import pytest

from app.services.document_service import _resolve_mime_type


def test_pdf_with_generic_browser_mime_type_is_accepted():
    content = b"%PDF-1.7\nexample"

    assert (
        _resolve_mime_type("report.pdf", "application/octet-stream", content)
        == "application/pdf"
    )


def test_pdf_mime_type_is_inferred_when_browser_supplies_none():
    content = b"%PDF-1.4\nexample"

    assert _resolve_mime_type("report.PDF", None, content) == "application/pdf"


def test_alternate_pdf_mime_type_is_normalized():
    content = b"%PDF-1.4\nexample"

    assert _resolve_mime_type("report.pdf", "application/x-pdf", content) == "application/pdf"


def test_fake_pdf_is_rejected():
    with pytest.raises(ValueError, match="does not appear to be a valid PDF"):
        _resolve_mime_type("report.pdf", "application/pdf", b"not a pdf")


def test_unsupported_extension_and_mime_type_are_rejected():
    with pytest.raises(ValueError, match="Unsupported file type"):
        _resolve_mime_type("archive.zip", "application/zip", b"PK")
