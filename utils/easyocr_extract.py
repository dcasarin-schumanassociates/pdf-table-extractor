# utils/easyocr_extract.py

import easyocr
import pandas as pd
import numpy as np

# Load English by default, add more languages as needed
reader = easyocr.Reader(['en'], gpu=False)

def extract_table_easyocr(image):
    result = reader.readtext(np.array(image), detail=1)

    if not result:
        return pd.DataFrame([["No text found"]])

    # Get bounding boxes and text
    boxes_text = []
    for (bbox, text, conf) in result:
        if text.strip():
            x_min = int(min([point[0] for point in bbox]))
            y_min = int(min([point[1] for point in bbox]))
            boxes_text.append(((x_min, y_min), text.strip()))

    # Sort vertically then horizontally
    items = sorted(boxes_text, key=lambda x: (x[0][1], x[0][0]))

    # Group into rows
    rows, current_row = [], []
    last_y = -9999
    tolerance = 15

    for (x, y), text in items:
        if abs(y - last_y) > tolerance:
            if current_row:
                rows.append(current_row)
            current_row = [text]
            last_y = y
        else:
            current_row.append(text)
    if current_row:
        rows.append(current_row)

    # Normalize row lengths
    max_cols = max(len(r) for r in rows)
    for r in rows:
        r += [""] * (max_cols - len(r))

    return pd.DataFrame(rows)
