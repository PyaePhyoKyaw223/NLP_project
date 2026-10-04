from fastapi import FastAPI

from app.routes.extract import router as extract_router
from app.routes.health import router as health_router
from app.routes.preprocess import router as preprocess_router

app = FastAPI(
    title="Myanmar NLP ML Service",
    description="Phase 3: PDF upload and text extraction service",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(extract_router)
app.include_router(preprocess_router)
