#https://github.com/tesseract-ocr/tessdata/blob/main/vie.traineddata
from pytesseract import image_to_string
from PIL import Image, ImageOps
image = Image.open(r"./img/viet.png" )
# Chuyển đổi sang grayscale và xử lý threshold
image = ImageOps.grayscale(image)
image = image.point(lambda x: 0 if x < 128 else 255, '1')
text = image_to_string(image, lang='eng+vie', config='--psm 3 --oem 3')
print(text)
