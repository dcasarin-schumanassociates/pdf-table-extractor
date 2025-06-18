import cv2
import numpy as np
from PIL import Image

def preprocess_image(pil_image):
    # Convert to grayscale
    image = np.array(pil_image.convert("L"))

    # Moderate resize (improves digit detection but avoids skew)
    image = cv2.resize(image, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_LINEAR)

    # Use standard Gaussian blur
    image = cv2.GaussianBlur(image, (3, 3), 0)

    # Binary threshold (not inverted)
    image = cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,  # ⚠️ This keeps table lines black
        15,
        10
    )

    return image
