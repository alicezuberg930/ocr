'''
pip install opencv-python
pip install matplotlib
pip install scipy
pip install pytesseract

install Tesseract : https://github.com/UB-Mannheim/tesseract/wiki
c:\Program Files\Tesseract-OCR\

Đây là ma trận pixel 20x17. Xin minh họa thuật toán GaussianBlur bằng cách tính ma trận Kernel Gaussian 
sau đó biến đổi ma trận pixel rồi vẽ ma trận Kernel Gaussian dạng hình chuông và hình đã biến đổi ra màn hình ạ
'''
import numpy as np
import matplotlib.pyplot as plt
#from scipy.ndimage import gaussian_filter
import scipy
from mpl_toolkits.mplot3d import Axes3D
import cv2

# Tạo kernel Gaussian 5x5
'''
Giá trị sigma (σ) trong Gaussian Blur là một tham số quan trọng điều khiển độ mờ của ảnh. 

Ý nghĩa toán học:
Sigma là độ lệch chuẩn của phân phối Gaussian (hàm phân phối chuẩn)
Công thức Gaussian 2D: G(x,y) = (1/(2πσ²)) * e^(-(x² + y²)/(2σ²))
Sigma càng lớn, đường cong Gaussian càng "phẳng" và "rộng" ra
Sigma càng nhỏ, đường cong Gaussian càng "nhọn" và "hẹp" lại


Ảnh hưởng đến kernel:
Với sigma = 1.0:
Pixel ở tâm kernel có trọng số cao nhất
Các pixel lân cận có trọng số giảm dần theo khoảng cách
Ở khoảng cách 1σ (1 pixel), trọng số giảm còn khoảng 61%
Ở khoảng cách 2σ (2 pixel), trọng số giảm còn khoảng 14%
Ở khoảng cách 3σ (3 pixel), trọng số gần như bằng 0

Tác động lên ảnh:
sigma = 1.0 tạo ra độ mờ vừa phải:
Đủ để làm mềm các cạnh sắc
Giảm nhiễu nhỏ
Nhưng vẫn giữ được các đặc trưng chính của ảnh

Lựa chọn giá trị sigma:
sigma nhỏ (< 1.0): làm mờ nhẹ, giữ nhiều chi tiết
sigma = 1.0: độ mờ cân bằng, phù hợp nhiều ứng dụng
sigma lớn (> 1.0): làm mờ mạnh, mất nhiều chi tiết

Trong ví dụ của chúng ta:
scipy.gaussian_filter dùng sigma = 1.0 đồng nhất
cv2.GaussianBlur dùng sigmaX = 1.5 và sigmaY = 1.0, tạo độ mờ khác nhau theo hai hướng
'''
def create_gaussian_kernel(size=5, sigma=1.0):
    '''
    Generates size evenly spaced points between -(size-1)/2 and (size-1)/2.
    This creates a coordinate axis centered around zero.
    Example (for size=5): ax = [-2, -1, 0, 1, 2].
    '''
    ax = np.linspace(-(size-1)/2., (size-1)/2., size)

    '''
    Creates two 2D grids (xx and yy) from the 1D coordinate axis ax. These grids represent the x-coordinates (xx) and y-coordinates (yy) for each point in the kernel.
    Example (for size=5):
    xx= [-2. -1.  0.  1.  2.]
        [[-2. -1.  0.  1.  2.]
        [-2. -1.  0.  1.  2.]
        [-2. -1.  0.  1.  2.]
        [-2. -1.  0.  1.  2.]
        [-2. -1.  0.  1.  2.]]
    yy= [[-2. -2. -2. -2. -2.]
        [-1. -1. -1. -1. -1.]
        [ 0.  0.  0.  0.  0.]
        [ 1.  1.  1.  1.  1.]
        [ 2.  2.  2.  2.  2.]]
        '''
    xx, yy = np.meshgrid(ax, ax)


    kernel = np.exp(-0.5 * (np.square(xx) + np.square(yy)) / np.square(sigma))
    return kernel / np.sum(kernel)

def my_filter2D(image, kernel):
    """
    Apply a 2D filter (kernel) to an image.
    
    Parameters:
        image (np.ndarray): Input image (grayscale or color).
        kernel (np.ndarray): Filter kernel (must be odd-sized).
        
    Returns:
        np.ndarray: Filtered image.
    """
    # Kiểm tra nếu ảnh là màu (3 chiều)
    if len(image.shape) == 3:
        # Nếu ảnh là màu, tách các kênh màu và áp dụng bộ lọc cho từng kênh
        filtered_image = np.zeros_like(image)
        for i in range(image.shape[2]):
            filtered_image[:, :, i] = my_filter2D(image[:, :, i], kernel)
        return filtered_image
    else:
        # Nếu ảnh là ảnh xám (2 chiều), áp dụng bộ lọc bình thường
        image_height, image_width = image.shape
        
        # Lấy kích thước của kernel
        kernel_height, kernel_width = kernel.shape
        
        # Tính toán các chỉ số để áp dụng kernel lên ảnh
        pad_height = kernel_height // 2
        pad_width = kernel_width // 2
        
        # Tạo ảnh đầu ra, khởi tạo với các giá trị 0
        output_image = np.zeros_like(image)
        
        # Thêm padding vào ảnh đầu vào để dễ dàng áp dụng kernel
        padded_image = np.pad(image, ((pad_height, pad_height), (pad_width, pad_width)), mode='constant', constant_values=0)
        
        # Duyệt qua các pixel của ảnh
        for i in range(image_height):
            for j in range(image_width):
                # Lấy vùng con của ảnh có cùng kích thước với kernel
                region = padded_image[i:i+kernel_height, j:j+kernel_width]
                
                # Tính giá trị pixel mới bằng phép nhân ma trận (kernel * region)
                output_image[i, j] = np.sum(region * kernel)
        
        return output_image
# Đọc ảnh và chuyển sang grayscale
img = cv2.imread(r"./img/Untitled.png")

# Tạo kernel Gaussian
kernel = create_gaussian_kernel(5, 1.0)

# Áp dụng Gaussian blur bằng các phương pháp khác nhau
#blurred_scipy = gaussian_filter(pixel_matrix, sigma=1.0)
blurred_scipy = scipy.ndimage.gaussian_filter(img, sigma=1.0)

#blurred_cv2 = cv2.filter2D(pixel_matrix, -1, kernel)
#blurred_cv2 = cv2.filter2D(img, -1, kernel)
blurred_cv2 = my_filter2D(img, kernel)

# Áp dụng cv2.GaussianBlur với các tham số cụ thể
ksize = (5, 5)  # Kernel size
sigmaX = 1.0    # Standard deviation in X direction
sigmaY = 1.0    # Standard deviation in Y direction
borderType = cv2.BORDER_REPLICATE  # Border type
#blurred_gaussian = cv2.GaussianBlur(pixel_matrix, ksize, sigmaX, sigmaY, borderType=borderType)
blurred_gaussian = cv2.GaussianBlur(img, ksize, sigmaX, sigmaY, borderType=borderType)

# Tạo figure với kích thước lớn hơn và tỷ lệ phù hợp
plt.figure(figsize=(15, 10))

# Dòng 1: Kernel, ảnh gốc và kết quả scipy
# 1. Vẽ ma trận kernel Gaussian dạng 3D
ax1 = plt.subplot(231, projection='3d')

#np.linspace tạo một mảng gồm 5 giá trị đều nhau từ -2 đến 2 sau đó np.meshgrid tạo lưới tọa độ từ các giá trị x và y.
x, y = np.meshgrid(np.linspace(-2, 2, 5), np.linspace(-2, 2, 5)) 

ax1.plot_surface(x, y, kernel, cmap='viridis')
ax1.set_title('Gaussian Kernel')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Value')

# 2. Vẽ ảnh gốc
#plt.subplot(232)
#plt.imshow(pixel_matrix, cmap='gray')
#plt.imshow(img)
#plt.title('Original Image')
#plt.colorbar()

# 3. Vẽ ảnh sau khi blur bằng scipy.ndimage
plt.subplot(233)
plt.imshow(blurred_scipy, cmap='gray')
plt.title('Blurred (scipy.gaussian_filter)')
plt.colorbar()

# Dòng 2: Kết quả cv2.filter2D và cv2.GaussianBlur
# 4. Vẽ ảnh sau khi blur bằng cv2.filter2D
plt.subplot(235)
plt.imshow(blurred_cv2, cmap='gray')
plt.title('Blurred (cv2.filter2D)')
plt.colorbar()

# 5. Vẽ ảnh sau khi blur bằng cv2.GaussianBlur
plt.subplot(232)
plt.imshow(blurred_gaussian, cmap='gray')
plt.title('Blurred (cv2.GaussianBlur)\nsigmaX=1.5, sigmaY=1.0')
plt.colorbar()

plt.tight_layout()
plt.show()

# In ra ma trận kernel
print("\nGaussian Kernel Matrix:")
print(kernel)