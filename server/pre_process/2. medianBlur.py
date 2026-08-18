import cv2
import matplotlib.pyplot as plt
import numpy as np

def my_medianBlur(image, kernel_size):
    """
    Apply a median blur to an image.
    
    Parameters:
        image (np.ndarray): The input image (grayscale or color).
        kernel_size (int): Size of the kernel (should be odd, e.g., 3, 5, 7).
        
    Returns:
        np.ndarray: The median blurred image.
    """
    # Đảm bảo kernel_size là số lẻ
    if kernel_size % 2 == 0:
        raise ValueError("Kernel size must be odd.")
    
    # Lấy kích thước ảnh
    image_height, image_width = image.shape[:2]
    
    # Tạo ảnh đầu ra với cùng kích thước
    output_image = np.zeros_like(image)
    
    # Tính toán bán kính của cửa sổ (kernel)
    radius = kernel_size // 2
    
    # Duyệt qua từng pixel trong ảnh
    for i in range(image_height):
        for j in range(image_width):
            # Tạo cửa sổ (kernel) xung quanh pixel hiện tại
            # Lấy phạm vi của cửa sổ (với padding để không ra ngoài ảnh)
            x_min = max(i - radius, 0)
            x_max = min(i + radius + 1, image_height)
            y_min = max(j - radius, 0)
            y_max = min(j + radius + 1, image_width)
            
            # Lấy các giá trị pixel trong cửa sổ
            window = image[x_min:x_max, y_min:y_max]
            
            # Nếu ảnh màu (3 chiều), xử lý từng kênh riêng biệt
            if len(window.shape) == 3:
                for k in range(window.shape[2]):
                    output_image[i, j, k] = np.median(window[:, :, k])
            else:
                # Nếu ảnh xám, lấy giá trị trung vị của cửa sổ
                output_image[i, j] = np.median(window)
    
    return output_image

# Load a noisy image
#img = cv2.imread(r"d:\training\Courses\ai\Text Extraction\code\Untitled.png" )
img = cv2.imread(r"./img/final_complex_noisy_image.jpg")

# Apply median blur with kernel size 5
median_blurred = cv2.medianBlur(img, 5)  
my_medianBlur_img = my_medianBlur(img, 5)  

# Display the results
plt.figure(figsize=(10, 5))
plt.subplot(2, 2, 1)
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title('Original Image')
plt.axis('off')

plt.subplot(2, 2, 2)
plt.imshow(cv2.cvtColor(median_blurred, cv2.COLOR_BGR2RGB))
plt.title('Median Blurred Image')
plt.axis('off')

plt.subplot(2, 2, 3)
plt.imshow(cv2.cvtColor(my_medianBlur_img, cv2.COLOR_BGR2RGB))
plt.title('My Median Blurred Image')
plt.axis('off')

plt.show()