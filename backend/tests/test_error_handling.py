from fastapi.testclient import TestClient

from app.core.errors import GeminiRateLimitedError, GeminiUnavailableError
from app.main import app
from app.routers.correction import get_gemini_service


class RaisingGeminiService:
    def __init__(self, exc: Exception):
        self._exc = exc

    def check_pronunciation_attempt(self, **kwargs):
        raise self._exc


def _override_with_raising(exc: Exception):
    app.dependency_overrides[get_gemini_service] = lambda: RaisingGeminiService(exc)


def _correct_request(client):
    return client.post(
        "/api/v1/correct",
        json={"target_sentence": "I am happy.", "spoken_text": "I am happy."},
    )


def test_rate_limited_gemini_call_returns_429_with_a_friendly_detail(client):
    _override_with_raising(GeminiRateLimitedError("429 RESOURCE_EXHAUSTED"))

    response = _correct_request(client)

    app.dependency_overrides.clear()
    assert response.status_code == 429
    assert "wait" in response.json()["detail"].lower()


def test_gemini_unavailable_returns_503_with_a_friendly_detail(client):
    _override_with_raising(GeminiUnavailableError("503 UNAVAILABLE"))

    response = _correct_request(client)

    app.dependency_overrides.clear()
    assert response.status_code == 503
    assert "trouble" in response.json()["detail"].lower()


def test_an_unexpected_exception_returns_a_generic_500_not_a_raw_traceback():
    # Starlette's default TestClient re-raises unhandled server exceptions
    # (for easier test debugging) even when a registered `Exception` handler
    # already formatted a response — raise_server_exceptions=False is what
    # makes it behave like a real client would and actually return that
    # response, which is what this test needs to check.
    raw_client = TestClient(app, raise_server_exceptions=False)
    _override_with_raising(RuntimeError("boom — something we didn't anticipate"))

    response = _correct_request(raw_client)

    app.dependency_overrides.clear()
    assert response.status_code == 500
    body = response.json()
    assert "detail" in body
    # The real exception text/traceback must never leak to the client.
    assert "boom" not in body["detail"]
