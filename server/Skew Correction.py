import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image
image = cv2.imread(r'd:\training\Courses\ai\Text Extraction\doc\skew.png', cv2.IMREAD_GRAYSCALE)

# Step 1: Preprocessing - Binarization
# Convert to binary image using adaptive thresholding
thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                               cv2.THRESH_BINARY, 11, 2)

# Step 2: Edge Detection
edges = cv2.Canny(thresh, 50, 150, apertureSize=3)

# Step 3: Hough Line Transform to detect skew angle
# Use the Hough Transform to detect straight lines in the image
lines = cv2.HoughLines(edges, 1, np.pi / 180, 150)

# Step 4: Calculate the skew angle
# If lines are detected, calculate the angle of the first detected line
if lines is not None:
    for rho, theta in lines[0]:
        angle = np.rad2deg(theta) - 90
        break
else:
    angle = 0

# Step 5: Rotate the image to correct the skew
# Get the image dimensions
(h, w) = image.shape[:2]
center = (w // 2, h // 2)

# Rotate the image to correct skew
rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
rotated_image = cv2.warpAffine(image, rotation_matrix, (w, h))

# Step 6: Show the results
fig, axs = plt.subplots(1, 3, figsize=(15, 5))

# Original Image
axs[0].imshow(image, cmap='gray')
axs[0].set_title('Original Image')
axs[0].axis('off')

# Edge Detected Image
axs[1].imshow(edges, cmap='gray')
axs[1].set_title('Edge Detection (Canny)')
axs[1].axis('off')

# Skew-Corrected Image
axs[2].imshow(rotated_image, cmap='gray')
axs[2].set_title(f'Skew Corrected (Angle: {angle:.2f} degrees)')
axs[2].axis('off')

plt.show()
