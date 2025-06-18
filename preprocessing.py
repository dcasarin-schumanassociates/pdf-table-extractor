import cv2
import numpy as np
from PIL import Image

def preprocess_image(pil_image):
    image = np.array(pil_image.convert("L"))  # grayscale
    image = cv2.adaptiveThreshold(
        image, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    return image
