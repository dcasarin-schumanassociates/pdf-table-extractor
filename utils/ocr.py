import pytesseract
import pandas as pd


def extract_cells_to_dataframe(image, boxes, lang="eng"):
    rows, current_row = [], []
    last_y = -9999
    tolerance = 10

    # Sort boxes top to bottom, then left to right
    boxes = sorted(boxes, key=lambda b: (b[1], b[0]))

    for x, y, w, h in boxes:
        cropped = image[y:y+h, x:x+w]
        text = pytesseract.image_to_string(cropped, config="--psm 7", lang=lang).strip()

        if abs(y - last_y) > tolerance:
            if current_row:
                rows.append(current_row)
            current_row = [text]
            last_y = y
        else:
            current_row.append(text)

    if current_row:
        rows.append(current_row)

    max_cols = max((len(r) for r in rows), default=0)
    for r in rows:
        r += [""] * (max_cols - len(r))

    return pd.DataFrame(rows)
