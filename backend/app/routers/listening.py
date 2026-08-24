from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.auth import verify_firebase_token
from app.core.config import Settings, get_settings
from app.services.gemini_service import GeminiService, ListeningExercise

router = APIRouter(prefix="/api/v1/listening", tags=["listening"], dependencies=[Depends(verify_firebase_token)])


class ListeningRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=1,
        description="The theme for this round — usually the learner's current lesson topic, same as Practice mode's topic.",
        examples=["Ordering food at a restaurant"],
    )


def get_gemini_service(settings: Settings = Depends(get_settings)) -> GeminiService:
    return GeminiService(settings)


@router.post("/generate", response_model=ListeningExercise)
def generate_listening_exercise(
    request: ListeningRequest,
    gemini_service: GeminiService = Depends(get_gemini_service),
) -> ListeningExercise:
    """One round of listening-comprehension practice: a short passage for the client to read aloud via text-to-speech, plus a multiple-choice comprehension question."""
    return gemini_service.generate_listening_exercise(topic=request.topic)
