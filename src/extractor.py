import pdfplumber

class PDFExtractor:
    def __init__(self):
        pass

    def extract_text(self, pdf_path):
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += " " + page_text
            text = " ".join(text.split())
        except Exception as e:
            print(f"Error extracting text: {e}")
        return text