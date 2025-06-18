import pytesseract
import pandas as pd

def extract_cells_to_dataframe(image, boxes, lang="eng"):
    """Run OCR on sorted boxes, group by rows with padding."""
    rows = []
    current_row = []
    last_y = -9999
    tolerance = 15

    boxes = sorted(boxes, key=lambda b: (b[1], b[0]))

    for x, y, w, h in boxes:
        crop = image[y:y+h, x:x+w]
        text = pytesseract.image_to_string(crop, config="--psm 7", lang=lang).strip()

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
        max_cols = max(len(r) for r in rows)
        for r in rows:
            r += [""] * (max_cols - len(r))
        return pd.DataFrame(rows)
    return pd.DataFrame()
