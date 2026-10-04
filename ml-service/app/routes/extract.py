from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.extract import ExtractTextResponse
from app.services.pdf_extractor import PDFExtractionError, extract_text_from_pdf_bytes

router = APIRouter(prefix="/api", tags=["extraction"])

_ALLOWED_PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}


def _is_pdf_upload(upload_file: UploadFile) -> bool:
    filename = upload_file.filename or ""
    suffix = Path(filename).suffix.lower()
    content_type = (upload_file.content_type or "").lower()

    if suffix == ".pdf":
        return True

    return content_type in _ALLOWED_PDF_CONTENT_TYPES


@router.post("/extract-text", response_model=ExtractTextResponse)
async def extract_text(file: UploadFile = File(...)) -> ExtractTextResponse:
    if not _is_pdf_upload(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are currently supported.",
        )

    pdf_bytes = await file.read()

    try:
        result = extract_text_from_pdf_bytes(pdf_bytes)
    except PDFExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return ExtractTextResponse(
        filename=file.filename or "uploaded.pdf",
        page_count=int(result["page_count"]),
        text=str(result["text"]),
    )
