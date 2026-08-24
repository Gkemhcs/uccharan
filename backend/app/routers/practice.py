from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.services.gemini_service import GeminiService, PracticeMessage, PracticeTurnResult

router = APIRouter(prefix="/api/v1/practice", tags=["practice"])


class PracticeTurnRequest(BaseModel):
    chat_id: str = Field(
        ...,
        min_length=1,
        description=(
            "Client-generated id (e.g. a UUID) identifying this one practice "
            "session — request are otherwise fully stateless (nothing is "
            "stored server-side), so this doesn't gate or look anything up; "
            "it exists so concurrent conversations from different learners "
            "or devices are always distinguishable in logs, and so each "
            "session has a stable identity if session persistence is added later."
        ),
        examples=["c3b1f7a0-6b8e-4b9b-8a3a-8f8c9a1f2e3d"],
    )
    topic: str = Field(
        ...,
        min_length=1,
        description=(
            "The learner's current lesson topic — the Android client's current "
            "roadmap day theme (e.g. 'Food & Ordering'). Practice is always tied "
            "to what was just taught; there is deliberately no free-pick scenario "
            "menu or open-ended 'no fixed topic' mode."
        ),
        examples=["Food & Ordering"],
    )
    history: list[PracticeMessage] = Field(default_factory=list)
    learner_message: str = Field(..., min_length=1)
    preferred_address_term: str | None = None
    native_language: str | None = None
    conversation_summary: str | None = Field(
        default=None,
        description="Durable facts folded out of earlier turns — echo back exactly what the previous /turn response returned.",
    )
    summarized_through_index: int = Field(
        default=0,
        ge=0,
        description="How much of `history` is already covered by conversation_summary — echo back exactly what the previous /turn response returned.",
    )


class SummarizeRequest(BaseModel):
    history: list[PracticeMessage] = Field(..., min_length=1)
    previous_summary: str | None = None


class SummarizeResponse(BaseModel):
    summary: str


def get_gemini_service(settings: Settings = Depends(get_settings)) -> GeminiService:
    return GeminiService(settings)


@router.post("/turn", response_model=PracticeTurnResult)
def practice_turn(
    request: PracticeTurnRequest,
    gemini_service: GeminiService = Depends(get_gemini_service),
) -> PracticeTurnResult:
    """Advance a roleplay practice conversation, built around the learner's current lesson topic, by one turn."""
    return gemini_service.continue_practice_conversation(
        topic=request.topic,
        history=request.history,
        learner_message=request.learner_message,
        preferred_address_term=request.preferred_address_term,
        native_language=request.native_language,
        conversation_summary=request.conversation_summary,
        summarized_through_index=request.summarized_through_index,
    )


@router.post("/summarize", response_model=SummarizeResponse)
def summarize_conversation(
    request: SummarizeRequest,
    gemini_service: GeminiService = Depends(get_gemini_service),
) -> SummarizeResponse:
    """Compresses older turns of a long conversation into a durable-facts note.

    The client calls this periodically as a practice conversation grows —
    see `GeminiService.summarize_conversation` for why this exists.
    """
    summary = gemini_service.summarize_conversation(
        history=request.history,
        previous_summary=request.previous_summary,
    )
    return SummarizeResponse(summary=summary)
