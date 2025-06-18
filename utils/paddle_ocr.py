from paddleocr import PaddleOCR
import pandas as pd
import numpy as np
import cv2
from collections import defaultdict

# Initialise OCR model
ocr_model = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

def extract_table_paddle(image):
    """
    Extract text using PaddleOCR and reconstruct a table-like structure based on bounding box clustering.
    """
    result = ocr_model.ocr(np.array(image), cls=True)

    if not result or not result[0]:
        return pd.DataFrame([["No OCR text found"]])

    # Collect bounding boxes and text
    cells = []
    for line in result[0]:
        box = line[0]  # List of 4 (x, y) points
        text = line[1][0].strip()
        if text:
            x_coords = [pt[0] for pt in box]
            y_coords = [pt[1] for pt in box]
            x_min, x_max = int(min(x_coords)), int(max(x_coords))
            y_min, y_max = int(min(y_coords)), int(max(y_coords))
            cells.append({'text': text, 'x': x_min, 'y': y_min, 'w': x_max - x_min, 'h': y_max - y_min})

    # Sort top-to-bottom, left-to-right
    cells = sorted(cells, key=lambda c: (c['y'], c['x']))

    # Group rows by Y (vertical clustering)
    row_clusters = []
    tolerance_y = 20

    for cell in cells:
        added = False
        for row in row_clusters:
            if abs(cell['y'] - row[0]['y']) <= tolerance_y:
                row.append(cell)
                added = True
                break
        if not added:
            row_clusters.append([cell])

    # Sort cells within each row left to right
    for row in row_clusters:
        row.sort(key=lambda c: c['x'])

    # Reconstruct table
    table = []
    for row in row_clusters:
        table.append([cell['text'] for cell in row])

    # Pad to equal columns
    max_len = max(len(r) for r in table)
    for r in table:
        r += [''] * (max_len - len(r))

    return pd.DataFrame(table)
