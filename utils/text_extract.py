import pdfplumber

def try_pdf_text_extraction(file_like_object):
    tables_by_page = []
    with pdfplumber.open(file_like_object) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            tables_by_page.append(tables)
    return tables_by_page
