import json
import shutil
from pathlib import Path
from typing import BinaryIO

import pytesseract
from fastapi import APIRouter, FastAPI, File, Form, HTTPException, UploadFile
from PIL import Image

from post_process import clean_ocr_text
from pre_process import process_image
from utils import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH, RESULTS_FOLDER, UPLOAD_CHUNK_SIZE, cuid_generator

router = APIRouter()

def image_extension(filename: str | None) -> str:
    extension = Path(filename or "").suffix.removeprefix(".").lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")
    return extension


def save_upload(source: BinaryIO, destination: Path) -> None:
    size = 0

    with destination.open("xb") as output:
        while chunk := source.read(UPLOAD_CHUNK_SIZE):
            size += len(chunk)
            if size > MAX_CONTENT_LENGTH:
                raise HTTPException(
                    status_code=413,
                    detail="File too large. Maximum size is 16 MB.",
                )
            output.write(chunk)


def extract_text(image_path: str, lang: str) -> str:
    with Image.open(image_path) as image:
        text = pytesseract.image_to_string(image, lang=lang)
    return clean_ocr_text(text)


def save_job_record(record_path: Path, record: dict[str, str]) -> None:
    temporary_path = record_path.with_suffix(".tmp")
    with temporary_path.open("x", encoding="utf-8") as output:
        json.dump(record, output, ensure_ascii=False, indent=2)
        output.write("\n")
    temporary_path.replace(record_path)


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/extract")
def extract(
    file: UploadFile = File(...),
    lang: str = Form(default="eng+vie"),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No selected file")

    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)

    job_id = cuid_generator()
    directory = RESULTS_FOLDER / job_id
    directory.mkdir()

    extension = image_extension(file.filename)
    original_filename = f"original.{extension}"
    processed_filename = f"processed.{extension}"
    original_path = directory / original_filename
    processed_path = directory / processed_filename
    completed = False

    try:
        save_upload(file.file, original_path)
        process_image(str(original_path), str(processed_path))
        text = extract_text(str(processed_path), lang)

        record = {
            "job_id": job_id,
            "text": text,
            "original_image": f"/static/results/{job_id}/{original_filename}",
            "processed_image": f"/static/results/{job_id}/{processed_filename}",
        }
        save_job_record(directory / f"{job_id}.json", record)
        completed = True
        return record
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except (pytesseract.TesseractError, pytesseract.TesseractNotFoundError) as error:
        raise HTTPException(
            status_code=500,
            detail=f"Tesseract OCR error: {error}",
        ) from error
    finally:
        file.file.close()
        if not completed:
            shutil.rmtree(directory, ignore_errors=True)


def register_routes(server: FastAPI):
    server.include_router(router)
    # server.middleware('http')(interceptor)
