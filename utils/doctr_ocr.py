import numpy as np
import pandas as pd
from doctr.models import ocr_predictor
from doctr.io import DocumentFile

# Load doctr model (first time downloads weights)
model = ocr_predictor(pretrained=True)

def extract_with_doctr(pil_image):
    """
    Run OCR using doctr and return text blocks as a DataFrame.
    """
    # Convert to numpy and run model
    doc = DocumentFile.from_images([np.array(pil_image)])
    result = model(doc)

    # Parse output
    lines = result.pages[0].blocks
    rows = []

    for block in lines:
        for line in block.lines:
            text_line = [word.value for word in line.words]
            rows.append(text_line)

    # Normalize row lengths
    max_len = max((len(r) for r in rows), default=0)
    for r in rows:
        r += [""] * (max_len - len(r))

    return pd.DataFrame(rows)
