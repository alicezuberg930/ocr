import cv2
from matplotlib import pyplot as plt
import numpy as np
'''
Hiệu quả của Histogram Equalization:
Tăng độ tương phản cho ảnh có độ tương phản thấp.
Phân phối lại giá trị pixel để chi tiết trong vùng tối hoặc sáng dễ nhìn hơn.
Ứng dụng trong các lĩnh vực như xử lý ảnh y tế (X-ray, CT), xử lý ảnh vệ tinh, và cải thiện chất lượng hình ảnh.
'''
def histogram_equalization(image):
    """
    Perform histogram equalization on a grayscale image.

    :param image: Input grayscale image (2D numpy array).
    :return: Equalized image (2D numpy array).
    """
    # Step 1: Compute the histogram
    '''
    Dùng để tính histogram (tần suất xuất hiện của các giá trị cường độ pixel).
    Đầu ra: Tần suất và biên của các khoảng giá trị.

    image.flatten(): Chuyển hình ảnh từ mảng 2D thành 1D để dễ tính toán.
    np.histogram(): Tính toán histogram của hình ảnh.
    bins=256: Số mức cường độ (0–255) cho ảnh xám.
    range=[0, 256]: Khoảng giá trị cường độ pixel.
    Kết quả:
    hist: Một mảng cho biết tần suất của từng mức cường độ pixel trong ảnh.
    bins: Các ranh giới của từng mức cường độ (0–255).
    '''
    hist, bins = np.histogram(image.flatten(), bins=256, range=[0, 256])
    
    # Step 2: Compute the cumulative distribution function (CDF)
    '''
    Tính tổng tích lũy của một mảng. Trong trường hợp này, nó tạo ra CDF của histogram.
    hist.cumsum(): Tính tổng tích lũy của histogram. Đây chính là CDF.
    cdf / cdf.max(): Chuẩn hóa CDF về khoảng [0, 1].
    Ý nghĩa CDF:
    Xác định tổng tần suất tích lũy từ các mức cường độ nhỏ hơn hoặc bằng một giá trị cụ thể.
    Giúp quyết định cách phân phối lại giá trị cường độ trong hình ảnh.    
    '''
    cdf = hist.cumsum()
    cdf_normalized = cdf / cdf.max()  # Normalize CDF
    
    # Step 3: Map the pixel values based on the CDF
    '''
    cdf[cdf > 0].min(): Lấy giá trị CDF đầu tiên khác 0. Điều này giúp tránh giá trị không hợp lệ khi chuẩn hóa.
    Chuẩn hóa CDF: Mọi giá trị trong CDF được ánh xạ về khoảng [0, 255] để khớp với không gian cường độ của ảnh.
    astype('uint8'): Chuyển giá trị về kiểu uint8 để phù hợp với định dạng ảnh.
    '''
    cdf_min = cdf[cdf > 0].min()  # First non-zero value in CDF
    cdf_mapped = (cdf - cdf_min) / (cdf.max() - cdf_min) * 255  # Normalize to [0, 255]
    cdf_mapped = cdf_mapped.astype('uint8')  # Convert to integer
    
    # Map the image using the CDF
    '''
    cdf_mapped[image]: Mỗi pixel trong ảnh gốc sẽ được ánh xạ sang giá trị mới dựa trên CDF đã chuẩn hóa.
    Kết quả: Tạo ra hình ảnh với cường độ pixel được phân phối đồng đều hơn, cải thiện độ tương phản.    
    '''    
    equalized_image = cdf_mapped[image]
    
    return equalized_image

# Load an image
image_path = r"./img/Untitled.png"  # Replace with your image file path
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Apply Histogram Equalization
equalized_image = cv2.equalizeHist(image)

custom_equalized_image = histogram_equalization(image)

# Plot Original vs Equalized
plt.figure(figsize=(10, 5))

plt.subplot(2, 2, 1)
plt.title("Original Image")
plt.imshow(image, cmap='gray')
plt.axis("off")

plt.subplot(2, 2, 2)
plt.title("Equalized Image")
plt.imshow(equalized_image, cmap='gray')
plt.axis("off")

plt.subplot(2, 2, 3)
plt.title("Custom Equalized Image")
plt.imshow(equalized_image, cmap='gray')
plt.axis("off")


plt.tight_layout()
plt.show()

# Save the Equalized Image
#output_path = "equalized_image.jpg"
#cv2.imwrite(output_path, equalized_image)
#print(f"Equalized image saved at: {output_path}")
