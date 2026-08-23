from app.main import app
from app.routers.correction import get_gemini_service
from app.services.gemini_service import CorrectionResult


class FakeGeminiService:
    """Stand-in for GeminiService so tests never make a real network call."""

    def __init__(self, result: CorrectionResult):
        self._result = result

    def check_pronunciation_attempt(self, target_sentence: str, spoken_text: str) -> CorrectionResult:
        return self._result


def _override_gemini(result: CorrectionResult):
    app.dependency_overrides[get_gemini_service] = lambda: FakeGeminiService(result)


def test_correct_attempt_returns_feedback(client):
    _override_gemini(CorrectionResult(is_correct=True, feedback="Well done!"))

    response = client.post(
        "/api/v1/correct",
        json={"target_sentence": "I am happy.", "spoken_text": "I am happy."},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {"is_correct": True, "feedback": "Well done!"}


def test_correct_attempt_rejects_empty_spoken_text(client):
    response = client.post(
        "/api/v1/correct",
        json={"target_sentence": "I am happy.", "spoken_text": ""},
    )

    assert response.status_code == 422
