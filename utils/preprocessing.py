import cv2
import numpy as np
from PIL import Image

def preprocess_image(pil_image):
    # Convert to grayscale
    image = np.array(pil_image.convert("L"))

    # Resize image (to improve small character detection)
    image = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    # Apply Gaussian blur to reduce noise
    image = cv2.GaussianBlur(image, (3, 3), 0)

    # Adaptive Thresholding
    image = cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,  # INVERT to detect white-on-dark headings better
        15,
        10
    )

    return image
