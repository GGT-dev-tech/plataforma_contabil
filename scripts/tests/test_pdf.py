import pdfplumber
import sys

def test_pdf(file_path):
    print(f"--- Parsing {file_path} ---")
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            print(f"Page {i}:")
            print(text)

test_pdf("test_data/extrato_sample.pdf")
test_pdf("test_data/razao_sample.pdf")
