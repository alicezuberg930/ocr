# app.py
import os
from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import pytesseract
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Global variables to store image paths
original_image_path = None
processed_image_path = None
current_image_path = None  # Track current image for text extraction

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def process_image(image_path, method='gaussian'):
    img = cv2.imread(image_path)
    
    if method == 'thresholding':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #cv2.THRESH_OTSU, đây là ngưỡng tối ưu do Otsu tính toán
        #Nếu bạn đặt thresh = 0 và sử dụng cv2.THRESH_OTSU, giá trị ngưỡng thresh bạn cung cấp sẽ bị bỏ qua

        #cv2.THRESH_BINARY:
        #Tạo ảnh nhị phân (Binary Image):
        #  Pixel > ngưỡng: Gán giá trị tối đa (maxval).
        #  Pixel ≤ ngưỡng: Gán giá trị 0
        # retval: Giá trị ngưỡng được sử dụng
        retval, processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)    

    elif method == 'skew':
        processed = skew(img)

    elif method == 'gaussian':
        #làm mờ (blur) ảnh bằng cách áp dụng bộ lọc Gaussian. Phương pháp này rất phổ biến trong xử lý ảnh để giảm nhiễu (noise) hoặc làm mịn ảnh trước các bước xử lý tiếp theo.
        processed = cv2.GaussianBlur(img, (5, 5), 0)
    elif method == 'median':
        processed = cv2.medianBlur(img, 5)
    elif method == 'bilateral':
        processed = cv2.bilateralFilter(img, 9, 75, 75)
    else:
        processed = img
        
    filename = os.path.basename(image_path)
    base_filename = filename.split('_')[-1]
    processed_path = os.path.join(app.config['UPLOAD_FOLDER'], f'processed_{base_filename}')
    cv2.imwrite(processed_path, processed)
    
    return processed_path


def get_image():
    global processed_image_path, original_image_path, current_image_path
    use_original = request.form.get('use_original') == 'true'
   
    if use_original and original_image_path:
        input_path = original_image_path
    elif processed_image_path and not use_original:
        input_path = processed_image_path
    elif original_image_path:
        input_path = original_image_path
    else:
        return jsonify({'error': 'No image available for processing'})
    return input_path

def extract_text(lang='vie'):
    input_path = get_image()

    # Load ảnh và apply nhận dạng bằng Tesseract OCR
    #text = pytesseract.image_to_string(Image.open(filename),lang='vie')    
    #text = pytesseract.image_to_string(input_path,lang='vie')    
    #text = pytesseract.image_to_string(input_path, lang, config='--psm 3 --oem 3')
    text = pytesseract.image_to_string(input_path, lang)
    ########

    return text


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global original_image_path, current_image_path
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        original_image_path = filepath
        current_image_path = filepath  # Set current image to original
        
        return jsonify({
            'original': f'/static/uploads/{filename}'
        })
    
    return jsonify({'error': 'Invalid file type'})

@app.route('/process', methods=['POST'])
def process():
    method = request.form.get('process_method', 'gaussian')
    input_path = get_image()

    global processed_image_path, current_image_path
    processed_image_path = process_image(input_path, method)
    current_image_path = processed_image_path  # Update current image to processed
    filename = os.path.basename(processed_image_path)
    
    return jsonify({
        'processed': f'/static/uploads/{filename}'
    })

@app.route('/extract', methods=['POST'])
def extract():
    lang = request.form.get('lang', 'eng+vie')  # Default to English + Vietnamese
    text = extract_text(lang)
    return jsonify({'text': text})

if __name__ == '__main__':
    app.run(debug=True, port=8080)