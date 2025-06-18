import cv2

def detect_table_cells(preprocessed_img):
    img_draw = cv2.cvtColor(preprocessed_img, cv2.COLOR_GRAY2BGR)
    inv_img = 255 - preprocessed_img

    # Morphological operations for line detection
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, preprocessed_img.shape[0] // 100))
    vertical_lines = cv2.erode(inv_img, vertical_kernel, iterations=3)
    vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=3)

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (preprocessed_img.shape[1] // 100, 1))
    horizontal_lines = cv2.erode(inv_img, horizontal_kernel, iterations=3)
    horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=3)

    # Combine horizontal and vertical lines
    table_mask = cv2.add(horizontal_lines, vertical_lines)

    # Detect contours
    contours, _ = cv2.findContours(table_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        aspect_ratio = w / h if h != 0 else 0
        if w > 40 and h > 20 and area > 1500 and 0.2 < aspect_ratio < 5:
            boxes.append((x, y, w, h))
            cv2.rectangle(img_draw, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Sort by top-to-bottom, then left-to-right
    return img_draw, sorted(boxes, key=lambda b: (b[1], b[0]))
