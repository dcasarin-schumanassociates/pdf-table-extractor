import pytesseract
import pandas as pd

def extract_cells_to_dataframe(image, boxes, lang="eng"):
    import numpy as np

    # Sort boxes top-to-bottom
    boxes = sorted(boxes, key=lambda b: b[1])

    rows = []
    row = []
    last_y = -1
    tolerance = 15  # row height grouping tolerance

    grid = []
    current_row = []

    for i, box in enumerate(boxes):
        x, y, w, h = box

        # Start new row if Y-distance exceeds tolerance
        if last_y == -1 or abs(y - last_y) < tolerance:
            current_row.append(box)
            last_y = y
        else:
            # sort current row by X (left to right)
            current_row = sorted(current_row, key=lambda b: b[0])
            grid.append(current_row)
            current_row = [box]
            last_y = y

    # append final row
    if current_row:
        current_row = sorted(current_row, key=lambda b: b[0])
        grid.append(current_row)

    # Build table row by row
    for row_boxes in grid:
        row_texts = []
        for x, y, w, h in row_boxes:
            cropped = image[y:y+h, x:x+w]
            text = pytesseract.image_to_string(cropped, config="--psm 6", lang=lang).strip()
            row_texts.append(text)
        rows.append(row_texts)

    # Normalize row lengths
    if rows:
        max_cols = max(len(r) for r in rows)
        for r in rows:
            r += [""] * (max_cols - len(r))
        return pd.DataFrame(rows)
    else:
        return pd.DataFrame()
