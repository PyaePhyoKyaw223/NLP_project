from fastapi import APIRouter, HTTPException, status

from app.schemas.preprocessing import PreprocessRequest, PreprocessResponse
from app.services.preprocessor import TextPreprocessingError, preprocess_text

router = APIRouter(prefix="/api", tags=["preprocessing"])


@router.post("/preprocess-text", response_model=PreprocessResponse)
async def preprocess_text_endpoint(payload: PreprocessRequest) -> PreprocessResponse:
    try:
        result = preprocess_text(payload.text)
    except TextPreprocessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return PreprocessResponse(
        original_text=result["original_text"],
        cleaned_text=result["cleaned_text"],
        sentence_count=result["sentence_count"],
        sentences=result["sentences"],
    )
