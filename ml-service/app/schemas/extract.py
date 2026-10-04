from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])


class ExtractTextResponse(BaseModel):
    filename: str
    page_count: int
    text: str
