import pytesseract
import pandas as pd

def extract_cells_to_dataframe(image, boxes, lang="eng"):
    rows, current_row = [], []
    last_y = -9999
    tolerance = 15  # vertical alignment threshold

    boxes = sorted(boxes, key=lambda b: (b[1], b[0]))  # y, then x

    for box in boxes:
        x, y, w, h = box
        cropped = image[y:y+h, x:x+w]
        text = pytesseract.image_to_string(cropped, config="--psm 6", lang=lang).strip()

        if abs(y - last_y) > tolerance:
            if current_row:
                rows.append(current_row)
            current_row = [text]
            last_y = y
        else:
            current_row.append(text)

    if current_row:
        rows.append(current_row)

    if rows:
        max_cols = max(len(row) for row in rows)
        for row in rows:
            row += [""] * (max_cols - len(row))
        return pd.DataFrame(rows)
    else:
        return pd.DataFrame()
