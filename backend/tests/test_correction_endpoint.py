from app.main import app
from app.routers.correction import get_gemini_service
from app.services.gemini_service import CorrectionResult


class FakeGeminiService:
    """Stand-in for GeminiService so tests never make a real network call."""

    def __init__(self, result: CorrectionResult):
        self._result = result
        self.last_call_kwargs: dict | None = None

    def check_pronunciation_attempt(self, **kwargs) -> CorrectionResult:
        self.last_call_kwargs = kwargs
        return self._result


def _override_gemini(result: CorrectionResult) -> FakeGeminiService:
    fake = FakeGeminiService(result)
    app.dependency_overrides[get_gemini_service] = lambda: fake
    return fake


def test_correct_attempt_returns_feedback(client):
    _override_gemini(CorrectionResult(is_correct=True, feedback="Well done!"))

    response = client.post(
        "/api/v1/correct",
        json={"target_sentence": "I am happy.", "spoken_text": "I am happy."},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {"is_correct": True, "feedback": "Well done!", "native_explanation": None}


def test_correct_attempt_passes_address_term_and_native_language_through(client):
    fake = _override_gemini(
        CorrectionResult(is_correct=True, feedback="Bagundi!", native_explanation="Chaala bagundi!")
    )

    response = client.post(
        "/api/v1/correct",
        json={
            "target_sentence": "I am happy.",
            "spoken_text": "I am happy.",
            "preferred_address_term": "Nanna",
            "native_language": "Telugu",
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["native_explanation"] == "Chaala bagundi!"
    assert fake.last_call_kwargs["preferred_address_term"] == "Nanna"
    assert fake.last_call_kwargs["native_language"] == "Telugu"


def test_correct_attempt_rejects_empty_spoken_text(client):
    response = client.post(
        "/api/v1/correct",
        json={"target_sentence": "I am happy.", "spoken_text": ""},
    )

    assert response.status_code == 422
