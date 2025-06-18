import cv2

def detect_table_cells(preprocessed_img):
    """Detect bounding boxes using contours – return sorted list of (x, y, w, h)."""
    img_draw = cv2.cvtColor(preprocessed_img, cv2.COLOR_GRAY2BGR)
    inv_img = 255 - preprocessed_img

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    morph = cv2.morphologyEx(inv_img, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 30 and h > 20:  # very light filtering
            boxes.append((x, y, w, h))
            cv2.rectangle(img_draw, (x, y), (x+w, y+h), (0, 255, 0), 1)

    return img_draw, sorted(boxes, key=lambda b: (b[1], b[0]))
