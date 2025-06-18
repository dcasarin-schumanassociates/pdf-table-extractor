import cv2
import numpy as np
from PIL import Image

def preprocess_image(pil_image):
    image = np.array(pil_image.convert("L"))
    image = cv2.resize(image, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_LINEAR)
    image = cv2.GaussianBlur(image, (3, 3), 0)
    image = cv2.adaptiveThreshold(
        image, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        15, 10
    )
    return image
