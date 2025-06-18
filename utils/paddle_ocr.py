# utils/paddle_ocr.py

from paddleocr import PaddleOCR
import pandas as pd
import numpy as np
import cv2

ocr_model = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

def extract_table_paddle(image):
    """
    Extracts text using PaddleOCR and attempts to reconstruct a DataFrame-like structure.
    """
    result = ocr_model.ocr(np.array(image), cls=True)
    
    if not result or not result[0]:
        return pd.DataFrame([["No OCR text found"]])

    # Extract bounding boxes and text
    boxes = []
    texts = []
    for line in result[0]:
        ((x0, y0), (x1, y1), (x2, y2), (x3, y3)) = line[0]
        text = line[1][0]
        x_min = int(min(x0, x1, x2, x3))
        y_min = int(min(y0, y1, y2, y3))
        boxes.append((x_min, y_min))
        texts.append(text)

    # Pair bounding boxes with text
    items = sorted(zip(boxes, texts), key=lambda x: (x[0][1], x[0][0]))

    # Try to group into rows based on vertical position
    rows = []
    current_row = []
    last_y = -9999
    tolerance = 20

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
