# utils/lp_ocr.py

import layoutparser as lp
import pytesseract
import pandas as pd
import numpy as np

def extract_table_with_layoutparser(image_pil, lang="eng"):
    """
    Use LayoutParser + TesseractAgent only (no Detectron2), for lightweight structured OCR.
    """
    image = np.array(image_pil.convert("RGB"))

    # Use LayoutParser's built-in TesseractAgent for layout-aware OCR
    agent = lp.TesseractAgent(languages=lang)

    layout = agent.detect(image)

    # Sort by top → bottom, then left → right
    layout = sorted(layout, key=lambda b: (b.y_1, b.x_1))

    rows = []
    current_row = []
    last_y = -9999
    tolerance = 15

    for block in layout:
        y = block.y_1
        text = block.text.strip()

        if abs(y - last_y) > tolerance:
            if current_row:
                rows.append(current_row)
            current_row = [text]
            last_y = y
        else:
            current_row.append(text)

    if current_row:
        rows.append(current_row)
