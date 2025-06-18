import pdfplumber

def try_pdf_text_extraction(file_bytes):
    tables_by_page = []

    with pdfplumber.open(file_bytes) as pdf:
        for page in pdf.pages:
            # Try table extraction (uses underlying layout)
            tables = page.extract_tables()
            tables_by_page.append(tables)

    return tables_by_page
