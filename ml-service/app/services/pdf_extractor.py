import re
from typing import Dict

import fitz


class PDFExtractionError(Exception):
    """Raised when PDF text extraction fails."""


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> Dict[str, object]:
    if not pdf_bytes:
        raise PDFExtractionError("The uploaded PDF file is empty.")

    try:
        document = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFExtractionError("Unable to read this PDF file.") from exc

    try:
        page_texts = []
        for page in document:
            page_texts.append(page.get_text("text"))

        extracted_text = "\n".join(page_texts)
        # Collapse repeated blank lines and trim surrounding whitespace.
        cleaned_text = re.sub(r"\n{3,}", "\n\n", extracted_text).strip()

        if not cleaned_text:
            raise PDFExtractionError(
                "No readable text was found in this PDF. "
                "This PDF may contain scanned images and OCR support is required."
            )

        return {
            "page_count": document.page_count,
            "text": cleaned_text,
        }
    finally:
        document.close()
