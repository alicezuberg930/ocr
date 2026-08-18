import cv2
import numpy as np
import matplotlib.pyplot as plt

# Tạo ảnh gốc nhỏ
img = np.array([[1, 2, 3]], dtype=np.uint8)

# Mở rộng viền với các loại borderType
constant = cv2.copyMakeBorder(img, 0, 0, 2, 2, cv2.BORDER_CONSTANT, value=0)
reflect = cv2.copyMakeBorder(img, 0, 0, 2, 2, cv2.BORDER_REFLECT)
reflect_101 = cv2.copyMakeBorder(img, 0, 0, 2, 2, cv2.BORDER_REFLECT_101)

# Hiển thị kết quả
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.title("BORDER_CONSTANT")
plt.imshow(constant, cmap='gray')
plt.axis("off")

plt.subplot(1, 3, 2)
plt.title("BORDER_REFLECT")
plt.imshow(reflect, cmap='gray')
plt.axis("off")

plt.subplot(1, 3, 3)
plt.title("BORDER_REFLECT_101")
plt.imshow(reflect_101, cmap='gray')
plt.axis("off")

plt.tight_layout()
plt.show()
