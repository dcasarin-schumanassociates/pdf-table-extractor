import cv2
import numpy as np

def detect_table_grid(preprocessed_img):
    img_draw = cv2.cvtColor(preprocessed_img, cv2.COLOR_GRAY2BGR)
    inv = 255 - preprocessed_img

    # Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    detect_horizontal = cv2.erode(inv, horizontal_kernel, iterations=2)
    horizontal_lines = cv2.dilate(detect_horizontal, horizontal_kernel, iterations=2)

    # Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    detect_vertical = cv2.erode(inv, vertical_kernel, iterations=2)
    vertical_lines = cv2.dilate(detect_vertical, vertical_kernel, iterations=2)

    # Combine lines
    table_mask = cv2.add(horizontal_lines, vertical_lines)

    # Find contours (cells will be bounded by these lines)
    contours, _ = cv2.findContours(table_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 50 and h > 20:  # tweak thresholds as needed
            boxes.append((x, y, w, h))
            cv2.rectangle(img_draw, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Sort into 2D grid by y and then x
    boxes = sorted(boxes, key=lambda b: (b[1], b[0]))  # top-down, then left-right
    return img_draw, boxes
