import io
import json
import os
import shutil
from datetime import datetime, timezone
import cv2
import numpy as np
import pytesseract
from pathlib import Path

from fastapi.responses import JSONResponse
from fastapi import APIRouter, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from PIL import Image

from utils import cuid_generator, interceptor, set_response, normalize_extension, image_bit_depth, job_directory, image_bit_depth, CLEANED_IMAGE_FILENAME, CLEANED_RESULTS_DIR, record_with_image_urls, is_valid_job_id, is_original_image_filename, image_media_type, image_response_headers

router = APIRouter()

UPLOAD_FOLDER = "static/uploads"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------------------------------------
# Global image state
#
# NOTE:
# This matches your Flask implementation.
# For production/multiple users, don't use global variables.
# -------------------------------------------------------

original_image_path: str | None = None
processed_image_path: str | None = None
current_image_path: str | None = None

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def skew(img: np.ndarray) -> np.ndarray:
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Convert to binary using Otsu threshold
    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )

    # Invert image
    thresh = cv2.bitwise_not(thresh)

    # Edge detection
    edges = cv2.Canny(
        thresh,
        50,
        150,
        apertureSize=3,
    )

    # Hough Line Transform
    lines = cv2.HoughLines(
        edges,
        1,
        np.pi / 180,
        200,
    )

    # If no lines are detected, return original grayscale image
    if lines is None:
        return gray

    angles = []

    for line in lines:
        rho, theta = line[0]

        # Convert radians -> degrees
        angle = np.degrees(theta) - 90

        angles.append(angle)

    if not angles:
        return gray

    # Median skew angle
    median_angle = np.median(angles)

    height, width = gray.shape

    center = (
        width // 2,
        height // 2,
    )

    # Rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(
        center,
        median_angle,
        1.0,
    )

    # Rotate image
    rotated_image = cv2.warpAffine(
        gray,
        rotation_matrix,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderValue=255,
    )

    return rotated_image


def process_image(
    image_path: str,
    method: str = "gaussian",
) -> str:
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError("Unable to read image")
    if method == "thresholding":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, processed = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY | cv2.THRESH_OTSU,
        )
    elif method == "skew":
        processed = skew(img)
    elif method == "gaussian":
        processed = cv2.GaussianBlur(img, (5, 5), 0)
    elif method == "median":
        processed = cv2.medianBlur(img, 5)
    elif method == "bilateral":
        processed = cv2.bilateralFilter(img, 9, 75, 75)
    else:
        processed = img

    filename = os.path.basename(image_path)

    # Keep the original behavior:
    # original: abc.jpg
    # processed: processed_abc.jpg
    base_filename = filename.split("_")[-1]

    processed_path = os.path.join(
        UPLOAD_FOLDER,
        f"processed_{base_filename}",
    )

    success = cv2.imwrite(processed_path, processed)

    if not success:
        raise ValueError("Failed to save processed image")
    return processed_path


def get_image(use_original: bool = False) -> str:
    global original_image_path
    global processed_image_path
    global current_image_path

    if use_original and original_image_path:
        return original_image_path
    if processed_image_path and not use_original:
        return processed_image_path
    if original_image_path:
        return original_image_path
    raise ValueError("No image available for processing")


def extract_text(
    lang: str = "vie",
    use_original: bool = False,
) -> str:
    input_path = get_image(use_original)
    text = pytesseract.image_to_string(Image.open(input_path), lang=lang)
    return text


@router.get('/health')
def health():
    return {'status': 'ok'}


@router.post('/upload')
async def upload(request: Request, file: UploadFile = File(...)):
    global original_image_path
    global current_image_path
    global processed_image_path

    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={
                "error": "No selected file"
            },
        )

    if not allowed_file(file.filename):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid file type"
            },
        )

    # Prevent paths such as ../../something.jpg
    filename = Path(file.filename).name

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename,
    )

    # Check file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_CONTENT_LENGTH:
        return JSONResponse(
            status_code=413,
            content={
                "error": "File too large. Maximum size is 16MB."
            },
        )

    # Save uploaded file
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer,
        )

    await file.close()

    original_image_path = filepath
    current_image_path = filepath

    # Reset previously processed image when uploading
    # another image.
    processed_image_path = None

    return {
        "original": f"/static/uploads/{filename}"
    }


@router.post("/process")
async def process(
    process_method: str = Form(default="gaussian"),
    use_original: str = Form(default="false"),
):
    global processed_image_path
    global current_image_path

    use_original_bool = use_original.lower() == "true"

    try:
        input_path = get_image(
            use_original=use_original_bool,
        )

        processed_image_path = process_image(
            input_path,
            process_method,
        )

        current_image_path = processed_image_path

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={
                "error": str(e)
            },
        )

    filename = os.path.basename(
        processed_image_path
    )

    return {
        "processed": f"/static/uploads/{filename}"
    }


@router.post("/extract")
async def extract(
    lang: str = Form(default="eng+vie"),
    use_original: str = Form(default="false"),
):
    use_original_bool = use_original.lower() == "true"

    try:
        text = extract_text(
            lang=lang,
            use_original=use_original_bool,
        )

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={
                "error": str(e)
            },
        )

    except pytesseract.TesseractError as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Tesseract OCR error: {str(e)}"
            },
        )

    return {
        "text": text
    }


def register_routes(server: FastAPI):
    server.include_router(router)
    server.middleware('http')(interceptor)
