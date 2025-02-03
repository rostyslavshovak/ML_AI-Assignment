import pytest
from src.extractor import PDFExtractor


# --- Fake classes to simulate pdfplumber behavior ---

class FakePage:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text

class FakePDF:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def fake_pdfplumber_open_success(pdf_path):
    """
    Simulate a successful open of a PDF file.
    Returns a FakePDF object with two pages.
    """
    pages = [FakePage("This is page 1."), FakePage("This is page 2.")]
    return FakePDF(pages)


def fake_pdfplumber_open_failure(pdf_path):
    """
    Simulate a failure when opening a PDF file.
    """
    raise Exception("Failed to open PDF")


def test_extract_text_success(monkeypatch):
    """
    Test that PDFExtractor.extract_text returns the expected text
    when pdfplumber.open works correctly.
    """
    import pdfplumber
    monkeypatch.setattr(pdfplumber, "open", fake_pdfplumber_open_success)

    extractor = PDFExtractor()
    result = extractor.extract_text("dummy_path.pdf")

    # Expected text is the concatenation of the pages.
    expected = "This is page 1. This is page 2."
    assert result == expected


def test_extract_text_failure(monkeypatch, capsys):
    """
    Test that PDFExtractor.extract_text returns an empty string when an exception is raised,
    and that it prints an error message.
    """
    import pdfplumber
    monkeypatch.setattr(pdfplumber, "open", fake_pdfplumber_open_failure)

    extractor = PDFExtractor()
    result = extractor.extract_text("dummy_path.pdf")

    captured = capsys.readouterr().out
    assert "Error extracting text:" in captured
    assert result == ""