"""Thin wrapper around the Gemini API for correction/tutoring calls.

Kept small and isolated on purpose: this is the one place that talks to
Gemini, so it's the one place tests mock out, and the one place we touch
if we ever add a fallback provider (e.g. Groq) or swap models.
"""

from google import genai
from pydantic import BaseModel

from app.core.config import Settings

CORRECTION_PROMPT_TEMPLATE = """You are an encouraging English speaking tutor.
The student was asked to say this target sentence:
"{target_sentence}"

Speech recognition heard them say:
"{spoken_text}"

Compare the two. Respond in this exact format, nothing else:
CORRECT: yes or no
FEEDBACK: one short, encouraging sentence explaining any mistake in plain language \
(grammar, word choice, or likely mispronunciation implied by the transcript difference). \
If it's correct, give a short positive remark instead.
"""


class CorrectionResult(BaseModel):
    is_correct: bool
    feedback: str


class GeminiService:
    def __init__(self, settings: Settings):
        self._client = genai.Client(api_key=settings.google_api_key)
        self._model = settings.gemini_model

    def check_pronunciation_attempt(self, target_sentence: str, spoken_text: str) -> CorrectionResult:
        prompt = CORRECTION_PROMPT_TEMPLATE.format(
            target_sentence=target_sentence,
            spoken_text=spoken_text,
        )
        response = self._client.models.generate_content(model=self._model, contents=prompt)
        return self._parse_response(response.text or "")

    @staticmethod
    def _parse_response(raw_text: str) -> CorrectionResult:
        is_correct = False
        feedback = "Sorry, I couldn't evaluate that attempt — please try again."

        for line in raw_text.splitlines():
            line = line.strip()
            if line.upper().startswith("CORRECT:"):
                is_correct = line.split(":", 1)[1].strip().lower().startswith("y")
            elif line.upper().startswith("FEEDBACK:"):
                feedback = line.split(":", 1)[1].strip()

        return CorrectionResult(is_correct=is_correct, feedback=feedback)
