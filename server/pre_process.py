import cv2
import numpy as np


MIN_DESKEW_ANGLE = 0.5
MAX_DESKEW_ANGLE = 15.0


def skew(img: np.ndarray) -> np.ndarray:
    if len(img.shape) == 2:
        gray = img
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )

    thresh = cv2.bitwise_not(thresh)

    edges = cv2.Canny(
        thresh,
        50,
        150,
        apertureSize=3,
    )

    lines = cv2.HoughLines(
        edges,
        1,
        np.pi / 180,
        200,
    )

    if lines is None:
        return gray

    angles = []

    for line in lines:
        rho, theta = line[0]

        angle = np.degrees(theta) - 90
        if -MAX_DESKEW_ANGLE <= angle <= MAX_DESKEW_ANGLE:
            angles.append(angle)

    if not angles:
        return gray

    median_angle = np.median(angles)

    if abs(median_angle) < MIN_DESKEW_ANGLE:
        return gray

    height, width = gray.shape
    center = (width // 2, height // 2)

    rotation_matrix = cv2.getRotationMatrix2D(
        center,
        median_angle,
        1.0,
    )

    return cv2.warpAffine(
        gray,
        rotation_matrix,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderValue=255,
    )


def process_image(image_path: str, processed_path: str) -> str:
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Unable to read image")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    deskewed = skew(gray)
    blurred = cv2.GaussianBlur(deskewed, (5, 5), 0)

    processed = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2,
    )

    success = cv2.imwrite(processed_path, processed)

    if not success:
        raise ValueError("Failed to save processed image")

    return processed_path
