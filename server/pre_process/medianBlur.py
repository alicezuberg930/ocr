import cv2
import matplotlib.pyplot as plt

# Load a noisy image
img = cv2.imread(r"d:\training\Courses\ai\Text Extraction\code\Untitled.png" )

# Apply median blur with kernel size 5
median_blurred = cv2.medianBlur(img, 5)  

# Display the results
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title('Original Image')
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(cv2.cvtColor(median_blurred, cv2.COLOR_BGR2RGB))
plt.title('Median Blurred Image')
plt.axis('off')

plt.show()