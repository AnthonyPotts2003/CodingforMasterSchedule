# test_pdf_parsing.py
import pdfplumber
from pathlib import Path

pdf_path = Path(r"G:\My Drive\Project Dashboard\Public\Master Schedule\Master Schedule.pdf")

if pdf_path.exists():
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            print(f"\n--- Page {page_num + 1} ---")
            text = page.extract_text()
            print(text[:500])  # Print first 500 characters
else:
    print("PDF not found!")
 

