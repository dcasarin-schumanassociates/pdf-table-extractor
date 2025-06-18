# utils/easyocr_extract.py

import easyocr
import numpy as np
import pandas as pd

_model_cache = {}

def extract_table_easyocr(image, lang="en"):
    """
    Run OCR on the image using EasyOCR with specified language.
    Group text elements into rows based on vertical alignment.
    """
    if lang not in _model_cache:
        _model_cache[lang] = easyocr.Reader([lang], gpu=False)

    reader = _model_cache[lang]
    result = reader.readtext(np.array(image))

    if not result:
        return pd.DataFrame([["No text found"]])

    elements = []
    for (bbox, text, confidence) in result:
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = bbox
        x_min = min(x0, x1, x2, x3)
        y_min = min(y0, y1, y2, y3)
        elements.append(((x_min, y_min), text))

    sorted_elements = sorted(elements, key=lambda e: (round(e[0][1] / 10), e[0][0]))

    rows = []
    current_y = -9999
    current_row = []

    for (x, y), text in sorted_elements:
        if abs(y - current_y) > 15:
            if current_row:
                rows.append(current_row)
            current_row = [text]
            current_y = y
        else:
            current_row.append(text)

    if current_row:
        rows.append(current_row)

    max_len = max(len(r) for r in rows)
    for r in rows:
        r += [""] * (max_len - len(r))

    return pd.DataFrame(rows)

