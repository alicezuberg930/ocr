import cv2
import numpy as np
import matplotlib.pyplot as plt

def skew(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    

    # Threshold the image (Convert to binary image)
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Invert the image (necessary for Hough Transform)
    #Lật ảnh nhị phân (đổi màu trắng thành đen và ngược lại). Điều này là cần thiết cho việc áp dụng Hough Transform sau này, vì Hough Transform tìm kiếm các đường sáng trên nền tối.
    thresh = cv2.bitwise_not(thresh)

    # Apply Canny edge detection to find edges in the image

    #Hàm Canny trả về một ảnh nhị phân (black-and-white), trong đó:
    #Màu trắng (255): Các điểm được xác định là biên (có gradient mạnh).
    #Màu đen (0): Các điểm không phải biên, nghĩa là có gradient yếu hoặc không có sự thay đổi độ sáng rõ rệt.

    #gradient là một đại lượng đo sự thay đổi của cường độ ánh sáng tại một pixel trong ảnh. 
    #Nếu gradient tại một điểm rất lớn, có nghĩa là sự thay đổi độ sáng tại điểm đó rất mạnh, 
    #và điều này thường chỉ ra rằng đó là biên (ranh giới giữa các khu vực có độ sáng khác nhau).

    #Ngưỡng dưới có thể được đặt là 50. Nếu một pixel có gradient nhỏ hơn 50 , thuật toán sẽ coi đây là không phải biên và loại bỏ pixel đó khỏi kết quả.
    #Ngưỡng trên có thể được đặt là 150. Nếu một pixel có gradient lớn hơn 150, thuật toán sẽ coi đây là biên mạnh và giữ lại pixel đó.
    #Nếu gradient nằm trong khoảng từ 50 đến 150, thuật toán sẽ kiểm tra xem pixel đó có liên kết với các biên mạnh không. Nếu có, nó sẽ được giữ lại; nếu không, nó sẽ bị loại bỏ.
    edges = cv2.Canny(thresh, 50, 150, apertureSize=3)

    # Use Hough Line Transform to detect lines in the image
    #Trong không gian Hough, một đường thẳng được biểu diễn bởi hai tham số:
    #𝜌 là khoảng cách từ gốc tọa độ đến đường thẳng được đo chính xác đến đơn vị 1 pixel
    #𝜃 là góc của đường thẳng so với trục hoành (trục x). Nếu độ phân giải của 𝜃 là 𝜋/180, nghĩa là bạn sẽ tìm kiếm các đường thẳng với góc chính xác đến 1 độ
    #Một đường thẳng trong không gian ảnh có thể được biểu diễn trong không gian Hough bởi một điểm duy nhất (𝜌,𝜃)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    # Get the angle of the detected lines
    angles = []
    for line in lines:
        rho, theta = line[0]
        angle = np.degrees(theta) - 90  # Convert from radians to degrees and adjust
        angles.append(angle)

    # Calculate the median angle
    median_angle = np.median(angles)

    # Rotate the image to correct the skew
    (height, width) = img.shape
    center = (width // 2, height // 2)

    #tạo ra ma trận xoay ảnh theo góc trung vị median_angle, với tâm là điểm trung tâm của ảnh.
    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)

    #áp dụng ma trận xoay để quay ảnh và trả về ảnh đã được chỉnh sửa
    rotated_image = cv2.warpAffine(img, rotation_matrix, (width, height), flags=cv2.INTER_CUBIC, borderValue=255)
    return rotated_image

# Load the image
image_path = r'./img/skew.png'  # Change this to the path of your image
#img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
img = cv2.imread(image_path)

rotated_image = skew(img)

# Display the original and rotated image
plt.figure(figsize=(10, 5))

# Original Image
plt.subplot(1, 2, 1)
plt.title("Original Image")
plt.imshow(img, cmap='gray')
plt.axis('off')

# Corrected Image
plt.subplot(1, 2, 2)
plt.title("Skew Corrected Image")
plt.imshow(rotated_image, cmap='gray')
plt.axis('off')

plt.show()
