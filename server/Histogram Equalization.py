import cv2
from matplotlib import pyplot as plt

# Load an image
image_path = r"d:\training\Courses\ai\Text Extraction\code\Untitled.png"  # Replace with your image file path
#image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
image = cv2.imread(image_path)

# Apply Histogram Equalization
equalized_image = cv2.equalizeHist(image)

# Plot Original vs Equalized
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.title("Original Image")
plt.imshow(image, cmap='gray')
plt.axis("off")

plt.subplot(1, 2, 2)
plt.title("Equalized Image")
plt.imshow(equalized_image, cmap='gray')
plt.axis("off")

plt.tight_layout()
plt.show()

# Save the Equalized Image
output_path = "equalized_image.jpg"
cv2.imwrite(output_path, equalized_image)
print(f"Equalized image saved at: {output_path}")
