from app.main import app
from app.routers.listening import get_gemini_service
from app.services.gemini_service import ListeningExercise


class FakeGeminiService:
    def __init__(self, result: ListeningExercise):
        self._result = result
        self.last_call_kwargs: dict | None = None

    def generate_listening_exercise(self, **kwargs) -> ListeningExercise:
        self.last_call_kwargs = kwargs
        return self._result


def _override_gemini(result: ListeningExercise) -> FakeGeminiService:
    fake = FakeGeminiService(result)
    app.dependency_overrides[get_gemini_service] = lambda: fake
    return fake


def test_generate_listening_exercise_returns_the_exercise(client):
    _override_gemini(
        ListeningExercise(
            passage="Hi, table for two please.",
            question="What did the speaker ask for?",
            options=["A table for two", "The bill", "A menu", "Directions"],
            correct_option_index=0,
            explanation="They said 'table for two'.",
        ),
    )

    response = client.post("/api/v1/listening/generate", json={"topic": "Ordering food at a restaurant"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["passage"] == "Hi, table for two please."
    assert body["correct_option_index"] == 0
    assert len(body["options"]) == 4


def test_generate_listening_exercise_passes_topic_through(client):
    fake = _override_gemini(
        ListeningExercise(passage="p", question="q", options=["a", "b"], correct_option_index=0, explanation="e"),
    )

    client.post("/api/v1/listening/generate", json={"topic": "Asking for directions"})

    app.dependency_overrides.clear()
    assert fake.last_call_kwargs["topic"] == "Asking for directions"


def test_generate_listening_exercise_rejects_empty_topic(client):
    response = client.post("/api/v1/listening/generate", json={"topic": ""})

    assert response.status_code == 422


def test_generate_listening_exercise_rejects_missing_authorization_header(client):
    from app.core.auth import verify_firebase_token

    app.dependency_overrides.pop(verify_firebase_token, None)

    response = client.post("/api/v1/listening/generate", json={"topic": "Ordering food"})

    assert response.status_code == 401
