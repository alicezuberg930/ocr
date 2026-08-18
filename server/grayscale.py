from pytesseract import image_to_string
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import cv2
import numpy as np

def to_gray(image):
    # Convert the PIL image to a NumPy array
    image_np = np.array(image)

    # Convert the image to grayscale
    # If the image has an alpha channel (RGBA), use cv2.COLOR_RGBA2GRAY
    # Otherwise, use cv2.COLOR_RGB2GRAY
    if image_np.shape[-1] == 4:  # RGBA
        gray_image = cv2.cvtColor(image_np, cv2.COLOR_RGBA2GRAY)
    else:  # RGB
        gray_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    return gray_image

def to_grayscale(image):
    return  ImageOps.grayscale(image)

image = Image.open(r"./img/viet-mau.png" )
gray_image = to_grayscale(image)

plt.figure(figsize=(10, 5))

# Original Image
plt.subplot(1, 2, 1)
plt.title("Original Image")
plt.imshow(image, cmap='gray')
plt.axis('off')

# Corrected Image
plt.subplot(1, 2, 2)
plt.title("Gray Image")
plt.imshow(gray_image, cmap='gray')
plt.axis('off')

plt.show()