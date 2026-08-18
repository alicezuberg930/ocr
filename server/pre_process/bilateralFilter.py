'''
Hàm này được sử dụng để áp dụng bộ lọc bilateral lên ảnh, một kỹ thuật lọc giúp làm mịn ảnh trong khi vẫn bảo tồn các cạnh.

Dưới đây là ý nghĩa của từng tham số:

image: Đây là hình ảnh đầu vào mà bạn muốn áp dụng bộ lọc. Nó có thể là một đối tượng numpy.ndarray đại diện cho hình ảnh.

9: Tham số này xác định đường kính của lân cận được sử dụng trong quá trình lọc. Nói một cách đơn giản, nó xác định kích thước của vùng xung quanh mỗi pixel sẽ được xem xét khi tính toán giá trị pixel mới. Giá trị 9 có nghĩa là một vùng 9x9 pixel xung quanh mỗi pixel sẽ được sử dụng.

75: Đây là tham số σ trong miền không gian. Nó kiểm soát mức độ ảnh hưởng của khoảng cách không gian giữa các pixel đến kết quả lọc. Giá trị càng lớn, ảnh hưởng của khoảng cách càng ít, nghĩa là các pixel ở xa nhau vẫn có thể ảnh hưởng đến nhau.

75: Đây là tham số σ trong miền giá trị. Nó kiểm soát mức độ ảnh hưởng của sự khác biệt về giá trị pixel (ví dụ: cường độ màu) đến kết quả lọc. Giá trị càng lớn, ảnh hưởng của sự khác biệt về giá trị pixel càng ít, nghĩa là các pixel có giá trị khác nhau vẫn có thể ảnh hưởng đến nhau.

Tóm lại:
Tham số đầu tiên xác định kích thước vùng lân cận.
Tham số thứ hai kiểm soát ảnh hưởng của khoảng cách.
Tham số thứ ba kiểm soát ảnh hưởng của sự khác biệt về giá trị pixel.
Bằng cách điều chỉnh các tham số này, bạn có thể kiểm soát mức độ làm mịn và bảo tồn cạnh của bộ lọc bilateral.

'''
import cv2
from matplotlib import pyplot as plt

# Đọc hình ảnh
image = cv2.imread(r"d:\training\Courses\ai\Text Extraction\code\Untitled.png")

# Áp dụng bộ lọc bilateral
filtered_image = cv2.bilateralFilter(image, 9, 75, 75)

# Hiển thị hình ảnh
plt.subplot(121),plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)),plt.title('Gốc')
plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(cv2.cvtColor(filtered_image, cv2.COLOR_BGR2RGB)),plt.title('Bilateral Filter')
plt.xticks([]), plt.yticks([])
plt.show()