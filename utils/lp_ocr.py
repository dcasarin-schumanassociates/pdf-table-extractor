import layoutparser as lp
import pytesseract
import pandas as pd
import numpy as np
import cv2


def extract_table_with_layoutparser(image_pil, lang="eng"):
    """
    Detects tables and cells using LayoutParser, then performs OCR
    and returns a structured DataFrame (rows x columns).
    """
    # Convert PIL to numpy
    image = np.array(image_pil.convert("RGB"))

    # Use pre-trained PubLayNet model (lightweight)
    model = lp.Detectron2LayoutModel(
        config_path="lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
    )

    # Detect layout blocks
    layout = model.detect(image)

    # Get only table blocks
    tables = lp.Layout([b for b in layout if b.type == "Table"])
    if not tables:
        return pd.DataFrame()  # nothing detected

    # We'll process just the first table for now
    table_block = tables[0]
    x1, y1, x2, y2 = map(int, table_block.coordinates)
    table_crop = image[y1:y2, x1:x2]

    # Detect text blocks (cells) within table region
    cell_model = lp.TesseractAgent(languages=lang)
    cell_layout = cell_model.detect(image[y1:y2, x1:x2])

    # Sort detected cells by row then column
    cells_sorted = sorted(cell_layout, key=lambda b: (b.block.y_1, b.block.x_1))

    rows = []
    current_row = []
    last_y = -9999
    tolerance = 15

    for block in cells_sorted:
        x, y, x2, y2 = map(int, block.block.points[0] + block.block.points[2])
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

    max_cols = max(len(r) for r in rows)
    for r in rows:
        r += [""] * (max_cols - len(r))

    return pd.DataFrame(rows)
