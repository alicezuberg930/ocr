# Re-import necessary libraries since the execution environment was reset
import cv2
from matplotlib import pyplot as plt

# Load the uploaded image
#image_path = r"d:\training\Courses\ai\Text Extraction\code\Untitled.png" 
#image_path = r"d:\training\Courses\ai\Text Extraction\doc\final_complex_noisy_image.jpg"
image_path = "./img/bilateral_demo_image.jpg"  # Thay bằng đường dẫn tới ảnh
image_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
image = cv2.imread(image_path)

# Apply different thresholding techniques
#Binary Threshold: Pixels are set to 255 (white) if their value is greater than 127, otherwise set to 0 (black).
_, binary_threshold = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

#Binary Inverted Threshold: Opposite of binary thresholding; pixels are set to 0 if their value is greater than 127, otherwise set to 255.
_, binary_inv_threshold = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)

#Truncate Threshold: Pixels above 127 are set to 127, while others remain unchanged.
_, trunc_threshold = cv2.threshold(image, 127, 255, cv2.THRESH_TRUNC)

#To Zero Threshold: Pixels below 127 are set to 0, while others remain unchanged.
_, tozero_threshold = cv2.threshold(image, 127, 255, cv2.THRESH_TOZERO)

#To Zero Inverted Threshold: Pixels above 127 are set to 0, while others remain unchanged
_, tozero_inv_threshold = cv2.threshold(image, 127, 255, cv2.THRESH_TOZERO_INV)

# Apply Adaptive Mean Thresholding
adaptive_mean_thresh = cv2.adaptiveThreshold(
    image_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
)

# Apply Adaptive Gaussian Thresholding
adaptive_gaussian_thresh = cv2.adaptiveThreshold(
    image_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
)
'''
retval (or threshold value):
It is the threshold value used during the operation.
For most thresholding types (e.g., cv2.THRESH_BINARY, cv2.THRESH_BINARY_INV, etc.), it will simply be the same as the value passed to the thresh parameter.
For cv2.THRESH_OTSU or cv2.THRESH_TRIANGLE, it is the automatically computed optimal threshold value, which is determined by the respective algorithm.
'''

# Plot the results
titles = [
    "Original Image",
    "Binary Threshold",
    "Binary Inverted Threshold",
    "Truncate Threshold",
    "To Zero Threshold",
    "To Zero Inverted Threshold",
    "Adaptive Mean Thresholding",
    "Adaptive Gaussian Thresholding"
]

images = [
    image,
    binary_threshold,
    binary_inv_threshold,
    trunc_threshold,
    tozero_threshold,
    tozero_inv_threshold,
    adaptive_mean_thresh,
    adaptive_gaussian_thresh
]


plt.figure(figsize=(12, 8))
for i in range(len(images)):
    plt.subplot(2, 4, i + 1)
    plt.imshow(images[i], cmap="gray")
    plt.title(titles[i])
    plt.axis("off")

plt.tight_layout()
plt.show()
