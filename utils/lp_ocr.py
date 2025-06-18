# utils/lp_ocr.py

import layoutparser as lp
import pytesseract
import pandas as pd
import numpy as np

def extract_table_with_layoutparser(image_pil, lang="eng"):
    """
    Use LayoutParser with TesseractAgent to extract text blocks and return a structured DataFrame.
    This version avoids Detectron2 and uses lightweight built-in OCR.
    """

    # Convert PIL image to numpy array
    image = np.array(image_pil.convert("RGB"))

    # Initialize Tesseract agent with selected language
    agent = lp.TesseractAgent(languages=lang)

    # Run layout-aware OCR
    layout = agent.detect(image)

    # Sort blocks by top-down, then left-right (based on top-left corner coordinates)
    layout = sorted(layout, key=lambda b: (b.coordinates[0][1], b.coordinates[0][0]))  # (y1, x1)

    rows = []
    current_row = []
    last_y = -9999
    tolerance = 15  # pixel vertical tolerance for grouping

    for block in layout:
        y = block.coordinates[0][1]
        text = block.text.strip()

        if not text:
            continue  # Skip empty blocks

        # If y-difference exceeds tolerance, start new row
        if abs(y - last_y) > tolerance:
            if current_row:
                rows.append(current_row)
            current_row = [text]
            last_y = y
        else:
            current_row.append(text)

    # Append last row
    if current_row:
        rows.append(current_row)

    # Normalise row lengths
    max_cols = max((len(row) for row in rows), default=0)
    for row in rows:
        row += [""] * (max_cols - len(row))

    return pd.DataFrame(rows)
