from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import pandas as pd

def extract_with_doctr(pdf_file_or_bytes, page_index=0):
    # Read bytes if a file-like object is passed
    if hasattr(pdf_file_or_bytes, "read"):
        pdf_file_or_bytes = pdf_file_or_bytes.read()

    # Load specific page only
    doc = DocumentFile.from_pdf(pdf_file_or_bytes)[page_index:page_index+1]

    # Load OCR model
    model = ocr_predictor(pretrained=True)

    result = model(doc)

    # Extract structured data from blocks
    blocks = []
    for block in result.pages[0].blocks:
        row = []
        for line in block.lines:
            line_text = " ".join([word.value for word in line.words])
            row.append(line_text)
        if row:
            blocks.append(row)

    # Normalise column count
    max_cols = max((len(row) for row in blocks), default=0)
    for row in blocks:
        row += [""] * (max_cols - len(row))

    return pd.DataFrame(blocks)
