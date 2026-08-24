from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.auth import verify_firebase_token
from app.core.config import Settings, get_settings
from app.services.gemini_service import CorrectionResult, GeminiService

router = APIRouter(prefix="/api/v1", tags=["correction"], dependencies=[Depends(verify_firebase_token)])


class CorrectionRequest(BaseModel):
    target_sentence: str = Field(..., min_length=1, examples=["I have been to the store yesterday."])
    spoken_text: str = Field(..., min_length=1, examples=["I have been to the store yesterday."])
    preferred_address_term: str | None = Field(
        default=None,
        description="How the student wants to be addressed, e.g. 'Nanna', 'Amma', or their name.",
        examples=["Nanna"],
    )
    native_language: str | None = Field(
        default=None,
        description="Student's native language name, for a bilingual explanation alongside the English one.",
        examples=["Telugu"],
    )
    focus_sounds: list[str] = Field(
        default_factory=list,
        description="This lesson's curriculum-authored target pronunciation sound(s), e.g. ['th']. When feedback is about a likely mispronunciation, the tutor names one of these specifically instead of describing the mismatch abstractly.",
        examples=[["th"]],
    )


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
        preferred_address_term=request.preferred_address_term,
        native_language=request.native_language,
        focus_sounds=request.focus_sounds,
    )
