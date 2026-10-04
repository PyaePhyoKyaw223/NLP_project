from pydantic import BaseModel, Field


class PreprocessRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw extracted Myanmar text to preprocess")


class PreprocessResponse(BaseModel):
    original_text: str
    cleaned_text: str
    sentence_count: int
    sentences: list[str]
