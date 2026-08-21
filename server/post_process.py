import re
import unicodedata


CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f\ufeff]")
HORIZONTAL_WHITESPACE = re.compile(r"[^\S\n]+")
EXCESSIVE_NEWLINES = re.compile(r"\n{3,}")


def clean_ocr_text(text: str) -> str:
    normalized = unicodedata.normalize("NFC", text)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = CONTROL_CHARACTERS.sub("", normalized)
    normalized = "\n".join(
        HORIZONTAL_WHITESPACE.sub(" ", line).strip()
        for line in normalized.split("\n")
    )
    return EXCESSIVE_NEWLINES.sub("\n\n", normalized).strip()
