import cv2

def detect_table_cells(preprocessed_img):
    """Detects table cells using combined vertical + horizontal line detection."""

    img_draw = cv2.cvtColor(preprocessed_img, cv2.COLOR_GRAY2BGR)
    inv_img = 255 - preprocessed_img  # we want white lines on black background

    # ---- Define kernels
    scale = 20  # tune this number based on PDF resolution (try 15–25)
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, preprocessed_img.shape[0] // scale))
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (preprocessed_img.shape[1] // scale, 1))

    # ---- Extract vertical lines
    vertical_lines = cv2.erode(inv_img, vertical_kernel, iterations=3)
    vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=3)

    # ---- Extract horizontal lines
    horizontal_lines = cv2.erode(inv_img, horizontal_kernel, iterations=3)
    horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=3)

    # ---- Combine to get table grid
    grid_mask = cv2.add(horizontal_lines, vertical_lines)

    # ---- Find contours
    contours, _ = cv2.findContours(grid_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if w > 30 and h > 20 and area > 1000:  # tune this if needed
            boxes.append((x, y, w, h))
            cv2.rectangle(img_draw, (x, y), (x+w, y+h), (0, 255, 0), 1)

    # ---- Sort by Y then X
    boxes = sorted(boxes, key=lambda b: (b[1], b[0]))

    return img_draw, boxes
