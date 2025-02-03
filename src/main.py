import os
import json
from extractor import PDFExtractor
from processor import json_structure, postprocess_snippets

def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_path = os.path.join(project_root, "data", "mit18_pset2.pdf")
    output_json = os.path.join(project_root, "data", "outputs_v1.json")

    extractor = PDFExtractor()
    text = extractor.extract_text(pdf_path)

    data = json_structure(text)
    postprocess_snippets(data)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()