from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.services.gemini_service import CorrectionResult, GeminiService

router = APIRouter(prefix="/api/v1", tags=["correction"])


class CorrectionRequest(BaseModel):
    target_sentence: str = Field(..., min_length=1, examples=["I have been to the store yesterday."])
    spoken_text: str = Field(..., min_length=1, examples=["I have been to the store yesterday."])


def get_gemini_service(settings: Settings = Depends(get_settings)) -> GeminiService:
    return GeminiService(settings)


@router.post("/correct", response_model=CorrectionResult)
def correct_attempt(
    request: CorrectionRequest,
    gemini_service: GeminiService = Depends(get_gemini_service),
) -> CorrectionResult:
    """Compare what the student said against the target sentence and return feedback."""
    return gemini_service.check_pronunciation_attempt(
        target_sentence=request.target_sentence,
        spoken_text=request.spoken_text,
    )
